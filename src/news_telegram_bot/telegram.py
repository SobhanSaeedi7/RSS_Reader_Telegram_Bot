import asyncio
import os

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from news_telegram_bot.rss import get_news, get_new_news
from news_telegram_bot.article import get_article_html, extract_article_text
from news_telegram_bot.llm import summary_chain
from news_telegram_bot.state import (
    load_state,
    save_state,
    get_chat_state,
)


load_dotenv()

CHANNEL_ID = os.getenv("TELEGRAM_CHAT_ID")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    state = await asyncio.to_thread(load_state)

    chat_state = get_chat_state(
        state,
        chat_id,
    )

    chat_state["active"] = True

    await asyncio.to_thread(
        save_state,
        state,
    )

    await update.message.reply_text(
        "سلام! ربات خلاصه‌سازی اخبار ورزشی آماده است. 🏐"
    )

    await check_news(
        context.bot,
        chat_id,
    )

    if not context.chat_data.get("news_job_started"):
        context.job_queue.run_repeating(
            check_news_job,
            interval=300,
            first=300,
            chat_id=chat_id,
            name=f"news_job_{chat_id}",
        )

        context.chat_data["news_job_started"] = True


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    state = await asyncio.to_thread(load_state)

    chat_state = get_chat_state(
        state,
        chat_id,
    )

    chat_state["active"] = False
    chat_state["last_news_links"] = {
        "varzesh3": None,
        "khabarvarzeshi": None,
        "kayhanvarzeshi": None,
    }

    await asyncio.to_thread(
        save_state,
        state,
    )

    current_jobs = context.job_queue.get_jobs_by_name(
        f"news_job_{chat_id}"
    )

    for job in current_jobs:
        job.schedule_removal()

    context.chat_data["news_job_started"] = False

    await update.message.reply_text(
        "ربات برای این چت متوقف و وضعیت اخبار ریست شد. 🔄"
    )


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

    last_news_links = chat_state["last_news_links"]

    new_news = await asyncio.to_thread(
        get_new_news,
        news,
        last_news_links,
    )

    if not new_news:
        print("No new news.")
        return

    print(f"Found {len(new_news)} new news.")

    for item in reversed(new_news):
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
            continue

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

        last_news_links[item["source"]] = item["link"]

        await asyncio.to_thread(
            save_state,
            state,
        )


async def check_news_job(context: ContextTypes.DEFAULT_TYPE):
    await check_news(
        context.bot,
        context.job.chat_id,
    )


def run_bot():
    token = os.getenv("TELEGRAM_BOT_TOKEN")

    application = (
        Application.builder()
        .token(token)
        .build()
    )

    application.add_handler(
        CommandHandler("start", start)
    )

    application.add_handler(
        CommandHandler("reset", reset)
    )

    application.run_polling()