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


def get_new_news(news, last_news_link):
    if last_news_link is None:
        return news[:5]

    new_news = []

    for item in news:
        if item["link"] == last_news_link:
            break

        new_news.append(item)

    return new_news
