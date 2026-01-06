RSS_FEEDS = {
    "bbc": "https://feeds.bbci.co.uk/news/rss.xml",
    "guardian": "https://www.theguardian.com/uk/rss",
    "sky": "https://feeds.skynews.com/feeds/rss/uk.xml",
    "independent": "https://www.independent.co.uk/news/uk/rss",
    "metro": "https://metro.co.uk/news/uk/feed/",
    "standard": "https://www.standard.co.uk/news/uk/rss",
    "itv": "https://www.itv.com/news/rss",
    "mirror": "https://www.mirror.co.uk/news/uk-news/rss.xml",
    "telegraph": "https://www.telegraph.co.uk/news/rss.xml",
    "times": "https://www.times-series.co.uk/news/rss/",
    "dailymail": "https://www.dailymail.co.uk/news/index.rss",
    "gbnews": "https://www.gbnews.com/feeds/news.rss",
    "reuters": "https://www.reutersagency.com/feed/?best-topics=uk",
    "ap": "https://apnews.com/apf-intlnews?format=feed",
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
    "dailymail": 1,
    "gbnews": 1,
    "reuters": 2,
    "ap": 2,
    "times": 2,
}

SOURCE_BIAS = {
    # UK
    "bbc": 0.0,
    "guardian": -0.5,
    "independent": -0.5,
    "telegraph": 0.5,
    "times": 0.5,
    "metro": 0.0,
    "standard": 0.0,
    "sky": 0.0,
    "telegraph": 0.5,
    "times": 0.5,
    "dailymail": 1.0,
    "gbnews": 1.0,
    "reuters": 0.0,
    "ap": 0.0,
}

CLUSTER_TIME_WINDOW_HOURS = 48