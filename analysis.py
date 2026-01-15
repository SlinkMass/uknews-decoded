import json
import re
from pathlib import Path
import spacy
from textstat import textstat
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk

# Ensure VADER is available
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    nltk.download('vader_lexicon')

nlp = spacy.load("en_core_web_sm")
sia = SentimentIntensityAnalyzer()

DATA_DIR = Path("./data")
STORIES_FILE = DATA_DIR / "stories.json"

PROPAGANDA_WORDS = {
    "loaded": ["brutal", "regime", "vowed", "heroic", "thugs", "surge", "shameful", "slammed", "stunning"],
    "fear": ["warns", "terrifying", "threat", "crisis", "emergency", "collapse", "imminent", "catastrophe"],
    "bias_labels": ["far-left", "far-right", "extremist", "woke", "elites", "establishment", "radical"],
    "idiomatic_attacks": ["betrayal", "knives out", "backstabbing", "sell-out", "clutching at straws"]
}

def get_lexical_metrics(text):
    """Calculates vocabulary richness and readability."""
    words = re.findall(r'\w+', text.lower())
    if not words: return 0, 0
    ttr = len(set(words)) / len(words)
    readability = textstat.flesch_reading_ease(text)
    return round(ttr, 2), round(readability, 2)

def detect_propaganda_signals(text):
    """
    Identifies 'persuasive' language density AND emotional intensity.
    Keeping function name same as requested.
    """
    text_low = text.lower()
    hits = {key: 0 for key in PROPAGANDA_WORDS}
    
    # Use word boundaries to avoid false positives (e.g., 'war' in 'forward')
    for category, words in PROPAGANDA_WORDS.items():
        for word in words:
            pattern = rf"\b{re.escape(word)}\b"
            hits[category] += len(re.findall(pattern, text_low))
            
    total_hits = sum(hits.values())
    word_count = len(text.split())
    
    # Calculate Emotional Intensity using VADER
    sentiment = sia.polarity_scores(text)
    # The 'compound' score is -1 (neg) to 1 (pos). 
    # Absolute value gives us 'intensity' regardless of direction.
    intensity = abs(sentiment['compound']) * 100 
    
    # We combine hit density and emotional intensity for a final 'signal'
    density = (total_hits / word_count) * 100 if word_count > 0 else 0
    final_score = round((density + (intensity / 10)), 2) # Weighted average
    
    return final_score, hits

def analyze_stories():
    if not STORIES_FILE.exists(): 
        return []
        
    with open(STORIES_FILE, "r", encoding="utf-8") as f:
        stories = json.load(f)

    results = []
    for story in [s for s in stories if len(s['articles']) >= 2]:
        story_insights = {
            "story_id": story["story_id"],
            "topic": story["topic"],
            "articles": []
        }

        for art in story['articles']:
            # We use the 'summary' and 'headline' for analysis if 'text' isn't in the dict
            text_to_analyze = art.get('text', f"{art['headline']} {art['summary']}")
            
            ttr, readability = get_lexical_metrics(text_to_analyze)
            prop_density, prop_breakdown = detect_propaganda_signals(text_to_analyze)
            
            # PRESERVE ALL ORIGINAL FIELDS
            enriched_article = {**art} 
            enriched_article.update({
                "lexical_richness": ttr,
                "readability_score": readability,
                "propaganda_density": prop_density,
                "primary_signal": max(prop_breakdown, key=prop_breakdown.get) if prop_density > 0 else "Neutral"
            })
            
            story_insights["articles"].append(enriched_article)
        results.append(story_insights)

    with open(STORIES_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"Analysis complete. VADER sentiment and lexical metrics updated.")
    return results

if __name__ == "__main__":
    analyze_stories()