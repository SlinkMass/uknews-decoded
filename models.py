from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
import numpy as np

class Article(BaseModel):
    id: str
    source: str
    headline: str
    summary: str
    url: str
    published_at: datetime
    bias_score: float
    embedding: Optional[np.ndarray] = None

    model_config = {
        "arbitrary_types_allowed": True  # allow np.ndarray
    }

class Story(BaseModel):
    story_id: str
    topic: str
    articles: List[Article]