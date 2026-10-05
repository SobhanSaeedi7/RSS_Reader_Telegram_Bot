from news_telegram_bot.rss import get_news
from news_telegram_bot.article import get_article_html, extract_article_text
from news_telegram_bot.llm import summary_chain


def main():
    news = get_news()

    first_news = news[0]

    html = get_article_html(first_news["link"])

    article_text = extract_article_text(html)

    if article_text is None:
        print("Could not extract article text.")
        return

    response = summary_chain.invoke({
        "article_text": article_text
    })

    print("Title:")
    print(first_news["title"])

    print("\nSummary:")
    print(response.content)


if __name__ == "__main__":
    main()