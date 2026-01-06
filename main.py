from fastapi import FastAPI, Query
from pathlib import Path
from datetime import datetime, timedelta
import json

from news import get_stories

# ========================
# App + Config
# ========================

app = FastAPI(title="UK News Decoded API")

DATA_DIR = Path("./data")
STORIES_FILE = DATA_DIR / "stories.json"

CACHE_TTL_MINUTES = 15  # ⏱ change this freely

# ========================
# Cache helpers
# ========================

def cache_exists() -> bool:
    return STORIES_FILE.exists()

def cache_age_minutes() -> float | None:
    if not cache_exists():
        return None
    mtime = datetime.fromtimestamp(STORIES_FILE.stat().st_mtime)
    return (datetime.utcnow() - mtime).total_seconds() / 60

def cache_is_stale() -> bool:
    age = cache_age_minutes()
    if age is None:
        return True
    return age > CACHE_TTL_MINUTES

# ========================
# API routes
# ========================

@app.get("/api/stories")
def read_stories(
    force_refresh: bool = Query(False, description="Force regeneration")
):
    """
    Returns stories.
    Uses cache unless stale or force_refresh=true.
    """
    should_refresh = force_refresh or cache_is_stale()

    stories = get_stories(force_refresh=should_refresh)

    filtered = [s for s in stories if len(s.articles) >= 2]

    return {
        "refreshed": should_refresh,
        "cache_age_minutes": cache_age_minutes(),
        "story_count": len(filtered),
        "stories": filtered,
    }

@app.post("/api/refresh")
def refresh_stories():
    """
    Force a refresh of stories.
    """
    stories = get_stories(force_refresh=True)
    return {
        "refreshed": True,
        "story_count": len(stories),
    }

@app.get("/api/meta")
def cache_metadata():
    """
    Cache status for debugging / UI display.
    """
    return {
        "cache_exists": cache_exists(),
        "cache_age_minutes": cache_age_minutes(),
        "cache_ttl_minutes": CACHE_TTL_MINUTES,
        "is_stale": cache_is_stale(),
    }

@app.get("/api/health")
def health_check():
    return {"status": "ok"}
