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

from news_telegram_bot.news_service import check_news
from news_telegram_bot.scheduler import ensure_news_job
from news_telegram_bot.channel import (
    active_on_channel,
    deactive_on_channel,
    handle_channel_link,
)
from news_telegram_bot.state import (
    load_state,
    save_state,
    get_chat_state,
)

load_dotenv()


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
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

    ensure_news_job(
        context,
        chat_id,
    )


async def reset(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
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

    application.add_handler(
        CommandHandler(
            "active_on_channel",
            active_on_channel,
        )
    )

    application.add_handler(
        CommandHandler(
            "deactive_on_channel",
            deactive_on_channel,
        )
    )

    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_channel_link,
        )
    )

    application.run_polling()