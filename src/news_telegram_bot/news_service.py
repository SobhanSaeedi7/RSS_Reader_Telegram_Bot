import asyncio

from news_telegram_bot.rss import get_news, get_new_news
from news_telegram_bot.article import (
    get_article_html,
    extract_article_text,
)
from news_telegram_bot.llm import summary_chain
from news_telegram_bot.state import (
    load_state,
    save_state,
)


async def process_and_send_news(
    bot,
    destination_id,
    item,
):
    print("\nProcessing:")
    print(item["title"])

    #Run network requests in a separate thread to keep the bot responsive.
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
        chat_id=destination_id,
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
            bot=bot,
            destination_id=chat_id,
            chat_id=chat_id,
            channel_id=None,
            last_news_links=chat_state["last_news_links"],
            news=news,
        )

    for channel_id, channel_state in chat_state["channels"].items():
        if not channel_state["active"]:
            continue

        print(
            f"\nChecking channel: "
            f"{channel_state['username']}"
        )

        await send_news_to_destination(
            bot=bot,
            destination_id=channel_id,
            chat_id=chat_id,
            channel_id=channel_id,
            last_news_links=channel_state["last_news_links"],
            news=news,
        )


async def send_news_to_destination(
    bot,
    destination_id,
    chat_id,
    channel_id,
    last_news_links,
    news,
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
        f"for destination {destination_id}."
    )

    # Reverse the list so older new articles are sent first
    for item in reversed(new_news):
        current_state = await asyncio.to_thread(
            load_state,
        )

        current_chat_state = current_state["chats"].get(
            str(chat_id)
        )

        if current_chat_state is None:
            print(
                "Chat state not found. "
                "Stopping news processing."
            )
            return

        if channel_id is None:
            is_active = current_chat_state["active"]

            current_last_news_links = (
                current_chat_state["last_news_links"]
            )

        else:
            current_channel_state = (
                current_chat_state["channels"].get(
                    str(channel_id)
                )
            )

            if current_channel_state is None:
                print(
                    "Channel state not found. "
                    "Stopping news processing."
                )
                return

            is_active = current_channel_state["active"]

            current_last_news_links = (
                current_channel_state["last_news_links"]
            )

        #Stop before processing the next article if the destination has been reset or deactivated.
        if not is_active:
            print(
                "Destination is inactive. "
                "Stopping news processing."
            )
            return

        success = await process_and_send_news(
            bot,
            destination_id,
            item,
        )

        if success:
            #Save the link only after the article has been successfully processed and sent.
            current_last_news_links[
                item["source"]
            ] = item["link"]

            await asyncio.to_thread(
                save_state,
                current_state,
            )