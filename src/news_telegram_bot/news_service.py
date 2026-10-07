import asyncio

from news_telegram_bot.rss import get_news, get_new_news
from news_telegram_bot.article import (
    get_article_html,
    extract_article_text,
)
from news_telegram_bot.llm import summary_chain
from news_telegram_bot.state import load_state, save_state


async def process_and_send_news(
    bot,
    chat_id,
    item,
):
    print("\nProcessing:")
    print(item["title"])

    html = await asyncio.to_thread(
        get_article_html,
        item["link"],
    )

    article_text = await asyncio.to_thread(
        extract_article_text,
        html,
        item["link"],
    )

    if article_text is None:
        print("Could not extract article text.")
        return False

    response = await asyncio.to_thread(
        summary_chain.invoke,
        {"article_text": article_text},
    )

    summary = response.content

    print("\nSummary:")
    print(summary)

    message = (
        f"📰 {item['title']}\n\n"
        f"{summary}\n\n"
        f"🔗 {item['link']}"
    )

    await bot.send_message(
        chat_id=chat_id,
        text=message,
    )

    return True


async def check_news(bot, chat_id):
    print("\nChecking for new news...")

    news = await asyncio.to_thread(get_news)

    if not news:
        print("No news found.")
        return

    state = await asyncio.to_thread(load_state)

    chat_state = state["chats"].get(str(chat_id))

    if chat_state is None:
        print("Chat state not found.")
        return

    if chat_state["active"]:
        await send_news_to_destination(
            bot,
            chat_id,
            chat_state["last_news_links"],
            news,
            "chat",
            state,
        )

    for channel_id, channel_state in chat_state["channels"].items():

        if not channel_state["active"]:
            continue

        print(
            f"\nChecking channel: "
            f"{channel_state['username']}"
        )

        await send_news_to_destination(
            bot,
            channel_id,
            channel_state["last_news_links"],
            news,
            "channel",
            state,
        )


async def send_news_to_destination(
    bot,
    destination_id,
    last_news_links,
    news,
    destination_type,
    state,
):
    new_news = await asyncio.to_thread(
        get_new_news,
        news,
        last_news_links,
    )

    if not new_news:
        return

    print(
        f"Found {len(new_news)} new news "
        f"for {destination_type}."
    )

    for item in reversed(new_news):

        success = await process_and_send_news(
            bot,
            destination_id,
            item,
        )

        if success:
            last_news_links[item["source"]] = item["link"]

            await asyncio.to_thread(
                save_state,
                state,
            )