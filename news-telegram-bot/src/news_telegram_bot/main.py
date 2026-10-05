from news_telegram_bot.rss import get_news
from news_telegram_bot.article import get_article_html, extract_article_text


def main():
    news = get_news()

    first_news = news[0]

    html = get_article_html(first_news["link"])

    article_text = extract_article_text(html)

    print("Title:")
    print(first_news["title"])

    print("\nArticle:")
    print(article_text)


if __name__ == "__main__":
    main()