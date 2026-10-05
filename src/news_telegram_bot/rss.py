import feedparser


RSS_URL = "https://www.varzesh3.com/rss/all"


def get_news():
    feed = feedparser.parse(RSS_URL)

    news = []

    for entry in feed.entries:
        news.append({
            "title": entry.get("title", ""),
            "link": entry.get("link", ""),
            "description": entry.get("description", ""),
        })

    return news