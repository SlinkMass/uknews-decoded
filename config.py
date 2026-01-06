RSS_FEEDS = {
    "bbc": "https://feeds.bbci.co.uk/news/rss.xml",
    "guardian": "https://www.theguardian.com/uk/rss",
    "sky": "https://feeds.skynews.com/feeds/rss/uk.xml",
    "independent": "https://www.independent.co.uk/news/uk/rss",
    "metro": "https://metro.co.uk/news/uk/feed/",
    "standard": "https://www.standard.co.uk/news/uk/rss",
    "itv": "https://www.itv.com/news/rss",
    "mirror": "https://www.mirror.co.uk/news/uk-news/rss.xml",
}

SOURCE_MIN_SHARED = {
    "bbc": 2,
    "guardian": 2,
    "sky": 2,
    "independent": 2,
    "itv": 2,
    "standard": 1,
    "metro": 1,
    "mirror": 1,
    "telegraph": 1,
}

CLUSTER_TIME_WINDOW_HOURS = 48