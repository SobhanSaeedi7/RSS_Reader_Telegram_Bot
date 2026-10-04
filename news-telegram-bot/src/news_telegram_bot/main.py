from news_telegram_bot.rss import get_news, get_new_news
from news_telegram_bot.state import load_state, save_state


def main():
    news = get_news()

    state = load_state()
    last_news_link = state["last_news_link"]

    new_news = get_new_news(news, last_news_link)

    print(f"Found {len(new_news)} new news.")

    for item in new_news:
        print("Title:", item["title"])
        print("Link:", item["link"])
        print("Description:", item["description"])
        print("-" * 50)

    if new_news:
        save_state(new_news[0]["link"])


if __name__ == "__main__":
    main()