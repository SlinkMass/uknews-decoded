import json
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict

import feedparser

from models import Article, Story
from config import RSS_FEEDS, SOURCE_MIN_SHARED

# ========================
# Config
# ========================

DATA_DIR = Path("./data")
STORIES_FILE = DATA_DIR / "stories.json"

MAX_MATCH_HOURS = 48

STOPWORDS = {
    "the", "a", "an", "and", "or", "to", "of", "in", "on", "for",
    "with", "after", "over", "as", "by", "from", "is", "are",
    "was", "were"
}

GENERIC_WORDS = {
    "says", "said", "pm", "president", "leader",
    "government", "uk", "us", "britain",
    "attack", "raid", "response", "warning",
    "man", "woman", "people", "police"
}

# ========================
# Orchestration
# ========================

def get_stories(force_refresh: bool = False) -> List[Story]:
    if STORIES_FILE.exists() and not force_refresh:
        with open(STORIES_FILE, "r", encoding="utf-8") as f:
            return [Story(**s) for s in json.load(f)]

    articles = fetch_articles()
    stories = build_bbc_baseline_stories(articles)

    DATA_DIR.mkdir(exist_ok=True)
    with open(STORIES_FILE, "w", encoding="utf-8") as f:
        json.dump(
            [s.dict() for s in stories],
            f,
            indent=2,
            ensure_ascii=False,
            default=str,
        )

    evaluate(stories)
    return stories

# ========================
# RSS ingestion
# ========================

def fetch_articles() -> List[Article]:
    articles = []

    for source_id, feed_url in RSS_FEEDS.items():
        feed = feedparser.parse(feed_url)

        for entry in feed.entries:
            published = getattr(entry, "published_parsed", None)
            published_at = (
                datetime(*published[:6])
                if published
                else datetime.utcnow()
            )

            articles.append(
                Article(
                    id=f"{source_id}-{entry.get('id', entry.link)}",
                    source=source_id,
                    headline=getattr(entry, "title", ""),
                    summary=getattr(entry, "summary", ""),
                    url=getattr(entry, "link", ""),
                    published_at=published_at,
                    entities=[],
                    bias_score=0.0,
                )
            )

    return articles

# ========================
# BBC baseline matching
# ========================

def build_bbc_baseline_stories(articles: List[Article]) -> List[Story]:
    bbc_articles = [a for a in articles if a.source == "bbc"]
    other_articles = [a for a in articles if a.source != "bbc"]

    stories: List[Story] = []

    # Create one story per BBC article
    for i, bbc in enumerate(bbc_articles):
        stories.append(
            Story(
                story_id=f"story-{i+1:03d}",
                topic=", ".join(list(extract_anchors(bbc.headline))[:4]),
                articles=[bbc],
            )
        )

    # Assign other articles to BBC stories
    for article in other_articles:
        anchors = extract_anchors(article.headline)
        required = SOURCE_MIN_SHARED.get(article.source, 2)

        best_story = None
        best_score = 0

        for story in stories:
            # ⏱ time constraint
            story_time = story.articles[0].published_at
            time_diff = abs(
                (article.published_at - story_time).total_seconds()
            ) / 3600
            if time_diff > MAX_MATCH_HOURS:
                continue

            # 🚫 same source twice
            if any(a.source == article.source for a in story.articles):
                continue

            story_anchors = extract_anchors(story.articles[0].headline)
            shared = anchors & story_anchors

            if len(shared) < required:
                continue

            # If only one anchor, require it to be strong
            if len(shared) == 1:
                anchor = next(iter(shared))
                if len(anchor) < 7:
                    continue

            if len(shared) > best_score:
                best_story = story
                best_score = len(shared)

        if best_story:
            best_story.articles.append(article)

    return stories

# ========================
# Anchor extraction
# ========================

def extract_anchors(text: str) -> set[str]:
    tokens = re.findall(r"[A-Za-z][A-Za-z\-]{2,}", text.lower())

    return {
        t for t in tokens
        if t not in STOPWORDS
        and t not in GENERIC_WORDS
        and len(t) > 4
    }

# ========================
# Evaluation
# ========================

def evaluate(stories: List[Story]):
    total_articles = sum(len(s.articles) for s in stories)
    grouped = sum(1 for s in stories if len(s.articles) > 1)

    print(f"[Eval] {total_articles} articles → {len(stories)} BBC stories")
    print(f"[Eval] Stories with matches: {grouped}")
    print(f"[Eval] Avg articles/story: {total_articles / max(len(stories),1):.2f}")

    for s in stories[:5]:
        print(f"- {s.story_id}: {s.topic} ({len(s.articles)})")

# ========================

if __name__ == "__main__":
    get_stories(force_refresh=True)
