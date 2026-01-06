from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from news import get_stories

app = FastAPI(title="UK News Decoded")

@app.get("/api/health")
def health():
    return {"status": "ok"}

@app.get("/api/stories")
def stories():
    """
    Returns clustered news stories as JSON.
    """
    return get_stories()