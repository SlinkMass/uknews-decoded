import json
import torch
from datetime import datetime
from pathlib import Path
from typing import List
from concurrent.futures import ThreadPoolExecutor

from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
import feedparser
from newspaper import Article as Scraper
from sentence_transformers import SentenceTransformer, util

from models import Article, Story
from config import RSS_FEEDS, SOURCE_BIAS
import analysis

# Initialize model
model = SentenceTransformer('all-MiniLM-L6-v2')

DATA_DIR = Path("./data")
STORIES_FILE = DATA_DIR / "stories.json"

# Settings for performance and accuracy
MAX_MATCH_HOURS = 48
SIMILARITY_THRESHOLD = 0.55  # Lowered slightly to be more 'liberal' with matches
BBC_DEDUPE_THRESHOLD = 0.85 # Merges near-identical BBC stories into one seed
ARTICLE_CAP = 40             # Limits articles per source for speed

def get_full_content(article_obj: Article) -> str:
    """Scrapes the body text. Limits to first 1000 chars for processing speed."""
    try:
        a = Scraper(article_obj.url, request_timeout=4)
        a.download()
        a.parse()
        if len(a.text) > 100:
            # We only need the start of the article for semantic context
            return f"{a.title} {a.text[:1000]}"
    except Exception:
        pass
    # Fallback to headline and summary if scraping fails
    return f"{article_obj.headline} {article_obj.summary}"

def build_smart_stories(articles: List[Article]) -> List[Story]:
    # 1. Apply Article Cap per source
    source_counts = {}
    capped_articles = []
    for a in articles:
        source_counts.setdefault(a.source, 0)
        if source_counts[a.source] < ARTICLE_CAP:
            capped_articles.append(a)
            source_counts[a.source] += 1

    bbc_articles = [a for a in capped_articles if a.source == "bbc"]
    other_articles = [a for a in capped_articles if a.source != "bbc"]

    # 2. Scrape & Encode BBC articles
    print(f"Scraping {len(bbc_articles)} BBC articles...")
    with ThreadPoolExecutor(max_workers=8) as executor:
        bbc_texts = list(executor.map(get_full_content, bbc_articles))
    
    # Generate embeddings in one batch
    raw_bbc_embeddings = model.encode(bbc_texts, convert_to_tensor=True)

    # 3. Deduplicate BBC stories (The "Venezuela Fix")
    # This prevents multiple BBC seeds from competing for the same Mirror/Guardian articles
    unique_stories = []
    unique_embeddings = []

    for i, bbc in enumerate(bbc_articles):
        is_duplicate = False
        if unique_embeddings:
            # Check if this BBC article is nearly identical to one we've already seeded
            scores = util.cos_sim(raw_bbc_embeddings[i], torch.stack(unique_embeddings))
            if torch.max(scores) > BBC_DEDUPE_THRESHOLD:
                is_duplicate = True
        
        if not is_duplicate:
            unique_stories.append(Story(
                story_id=f"story-{len(unique_stories)+1:03d}",
                topic=bbc.headline,
                articles=[bbc]
            ))
            unique_embeddings.append(raw_bbc_embeddings[i])

    print(f"Created {len(unique_stories)} unique BBC seeds (merged {len(bbc_articles) - len(unique_stories)} duplicates).")

    # 4. Scrape & Encode Other articles
    print(f"Scraping {len(other_articles)} other articles...")
    with ThreadPoolExecutor(max_workers=12) as executor:
        other_texts = list(executor.map(get_full_content, other_articles))
    
    other_embeddings = model.encode(other_texts, convert_to_tensor=True)
    seed_tensor = torch.stack(unique_embeddings)

    # 5. Batch Comparison
    cosine_matrix = util.cos_sim(other_embeddings, seed_tensor)

    for i, other in enumerate(other_articles):
        best_score, best_idx = torch.max(cosine_matrix[i], dim=0)
        
        if best_score.item() > SIMILARITY_THRESHOLD:
            target_story = unique_stories[best_idx.item()]
            
            # Time constraint
            time_diff = abs((other.published_at - target_story.articles[0].published_at).total_seconds()) / 3600
            
            if time_diff < MAX_MATCH_HOURS:
                # Avoid duplicate sources in one story
                if not any(a.source == other.source for a in target_story.articles):
                    target_story.articles.append(other)

    return unique_stories

def get_stories(force_refresh: bool = False) -> List[Story]:
    if STORIES_FILE.exists() and not force_refresh:
        with open(STORIES_FILE, "r", encoding="utf-8") as f:
            return [Story(**s) for s in json.load(f)]

    print("Fetching RSS feeds...")
    raw_articles = []
    for source_id, feed_url in RSS_FEEDS.items():
        feed = feedparser.parse(feed_url)
        for entry in feed.entries:
            published = getattr(entry, "published_parsed", None)
            dt = datetime(*published[:6]) if published else datetime.utcnow()
            raw_articles.append(Article(
                id=f"{source_id}-{entry.get('id', entry.link)}",
                source=source_id,
                headline=getattr(entry, "title", ""),
                summary=getattr(entry, "summary", ""),
                url=getattr(entry, "link", ""),
                published_at=dt,
                entities=[],
                bias_score=SOURCE_BIAS.get(source_id, 0.0),
            ))

    stories = build_smart_stories(raw_articles)

    DATA_DIR.mkdir(exist_ok=True)
    with open(STORIES_FILE, "w", encoding="utf-8") as f:
        json.dump([s.dict() for s in stories], f, indent=2, ensure_ascii=False, default=str)

    print(f"Final results: {len(stories)} stories generated.")
    return stories

def process_and_analyze_stories(raw_stories):
    processed_stories = []
    
    for story_data in raw_stories:
        new_story = Story(story_id=story_data['id'], topic=story_data['topic'])
        
        for art in story_data['articles']:
            # Perform the analysis on the fly
            richness, reading_ease = analysis.get_lexical_metrics(art['text'])
            signal_density, signals = analysis.detect_narrative_signals(art['text'])
            
            # Map the highest signal hit to a label
            top_signal = max(signals, key=signals.get) if signal_density > 0 else "Balanced"

            analyzed_article = Article(
                **art,
                lexical_richness=richness,
                readability_score=reading_ease,
                loaded_language_density=signal_density,
                primary_signal=top_signal
            )
            new_story.articles.append(analyzed_article)
            
        processed_stories.append(new_story)
    
    return processed_stories

if __name__ == "__main__":
    get_stories(force_refresh=True)