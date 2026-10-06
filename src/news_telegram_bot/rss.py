import feedparser

RSS_SOURCES = {
    "varzesh3": "https://www.varzesh3.com/rss/all",
    "khabarvarzeshi": "https://www.khabarvarzeshi.com/rss",
    "kayhanvarzeshi": "https://kayhanvarzeshi.ir/fa/rss/allnews",
}


def get_news():
    news = []

    for source, rss_url in RSS_SOURCES.items():
        feed = feedparser.parse(rss_url)

        for entry in feed.entries:
            news.append({
                "source": source,
                "title": entry.get("title", ""),
                "link": entry.get("link", ""),
                "description": entry.get("description", ""),
            })

    return news


def get_new_news(news, last_news_links):
    new_news = []

    sources = set(item["source"] for item in news)

    for source in sources:
        source_news = [
            item for item in news
            if item["source"] == source
        ]

        last_news_link = last_news_links.get(source)

        if last_news_link is None:
            new_news.extend(source_news[:2])
            continue

        for item in source_news:
            if item["link"] == last_news_link:
                break

            new_news.append(item)

    return new_news