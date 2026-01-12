import json
import re
from pathlib import Path
import spacy
from textstat import textstat # pip install textstat

nlp = spacy.load("en_core_web_sm")

DATA_DIR = Path("./data")
STORIES_FILE = DATA_DIR / "stories.json"
INSIGHTS_FILE = DATA_DIR / "deep_insights.json"

# Expanded News Lexicons
# analysis.py - Updated Lexicon
PROPAGANDA_WORDS = {
    "loaded": [
        "brutal", "regime", "vowed", "heroic", "thugs", "surge", "shameful", 
        "outrageous", "fury", "scramble", "outcry", "lifeline", "rescue", 
        "takedown", "u-turn", "hammered", "slammed", "stunning"
    ],
    "fear": [
        "warns", "terrifying", "threat", "crisis", "emergency", "collapse", 
        "danger", "imminent", "doom", "catastrophe", "meltdown"
    ],
    "bias_labels": [
        "far-left", "far-right", "extremist", "woke", "elites", "establishment",
        "ministers", "bureaucrats", "lefty", "radical"
    ],
    "idiomatic_attacks": [
        "chickens have come home to roost", "betrayal", "knives out", 
        "backstabbing", "sell-out", "clutching at straws"
    ]
}
def get_lexical_metrics(text):
    """Calculates how complex and 'rich' the writing is."""
    # Type-Token Ratio (Vocabulary Richness)
    words = re.findall(r'\w+', text.lower())
    if not words: return 0, 0
    ttr = len(set(words)) / len(words)
    
    # Reading Ease (Flesch-Kincaid)
    # 0-30: Very Hard (Academic), 60-70: Standard, 90-100: Very Easy
    readability = textstat.flesch_reading_ease(text)
    
    return round(ttr, 2), round(readability, 2)

def detect_propaganda_signals(text):
    """Identifies the density of 'persuasive' language."""
    text_low = text.lower()
    hits = {key: 0 for key in PROPAGANDA_WORDS}
    
    for category, words in PROPAGANDA_WORDS.items():
        for word in words:
            hits[category] += text_low.count(word)
            
    total_hits = sum(hits.values())
    # Normalize by word count to get 'Density'
    word_count = len(text.split())
    density = (total_hits / word_count) * 100 if word_count > 0 else 0
    
    return round(density, 2), hits

def analyze_stories():
    if not STORIES_FILE.exists(): 
        return []
        
    with open(STORIES_FILE, "r") as f:
        stories = json.load(f)

    results = []
    # Process stories with 2+ articles
    for story in [s for s in stories if len(s['articles']) >= 2]:
        story_insights = {
            "story_id": story["story_id"],
            "topic": story["topic"],
            "articles": []
        }

        for art in story['articles']:
            # 1. Run the analysis logic
            text = f"{art['headline']} {art['summary']}"
            ttr, readability = get_lexical_metrics(text)
            prop_density, prop_breakdown = detect_propaganda_signals(text)
            
            # 2. PRESERVE ALL ORIGINAL FIELDS AND ADD NEW ONES
            # We take everything currently in the 'art' dict and append our new metrics
            enriched_article = {
                **art, # This preserves bias_score, summary, url, published_at, etc.
                "lexical_richness": ttr,
                "readability_score": readability,
                "propaganda_density": prop_density,
                "primary_signal": max(prop_breakdown, key=prop_breakdown.get) if prop_density > 0 else "None"
            }
            
            story_insights["articles"].append(enriched_article)
            
        results.append(story_insights)

    # Overwrite the stories file or write to insights file as per your setup
    # If your API reads from stories.json, you might want to overwrite that instead
    with open(STORIES_FILE, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Analysis complete. All original fields preserved + linguistic metrics added.")
    
    return results

if __name__ == "__main__":
    analyze_stories()