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
    get_channel_state,
    reset_channel_state,
)


load_dotenv()

CHANNEL_ID = os.getenv("TELEGRAM_CHAT_ID")


def ensure_news_job(context, chat_id):
    if context.chat_data.get("news_job_started"):
        return

    context.job_queue.run_repeating(
        check_news_job,
        interval=300,
        first=300,
        chat_id=chat_id,
        name=f"news_job_{chat_id}",
    )

    context.chat_data["news_job_started"] = True


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


    if chat_state["active"]:

        last_news_links = chat_state["last_news_links"]

        new_news = await asyncio.to_thread(
            get_new_news,
            news,
            last_news_links,
        )

        if new_news:
            print(
                f"Found {len(new_news)} new news for chat."
            )

            for item in reversed(new_news):

                success = await process_and_send_news(
                    bot,
                    chat_id,
                    item,
                )

                if success:
                    last_news_links[item["source"]] = item["link"]

                    await asyncio.to_thread(
                        save_state,
                        state,
                    )


    for channel_id, channel_state in chat_state["channels"].items():

        if not channel_state["active"]:
            continue

        print(
            f"\nChecking channel: "
            f"{channel_state['username']}"
        )

        last_news_links = channel_state["last_news_links"]

        new_news = await asyncio.to_thread(
            get_new_news,
            news,
            last_news_links,
        )

        if not new_news:
            continue

        print(
            f"Found {len(new_news)} new news "
            f"for channel."
        )

        for item in reversed(new_news):

            success = await process_and_send_news(
                bot,
                chat_id,
                item,
            )

            if success:
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


async def active_on_channel(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    context.user_data["channel_action"] = "activate"

    await update.message.reply_text(
        "لطفاً پس از اضافه کردن ربات به کانال، "
        "لینک کانال را ارسال کنید:"
    )


async def deactive_on_channel(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    context.user_data["channel_action"] = "deactivate"

    await update.message.reply_text(
        "لطفاً لینک کانالی که می‌خواهید غیرفعال شود را ارسال کنید:"
    )
    

async def handle_channel_link(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    action = context.user_data.get("channel_action")

    if not action:
        return

    link = update.message.text.strip()

    if not link.startswith("https://t.me/"):
        await update.message.reply_text(
            "لطفاً لینک معتبر کانال را به صورت "
            "https://t.me/... ارسال کنید."
        )
        return

    username = "@" + link.removeprefix(
        "https://t.me/"
    ).strip("/")

    try:
        channel = await context.bot.get_chat(username)
    except Exception:
        await update.message.reply_text(
            "نتوانستم کانال را پیدا کنم یا به آن دسترسی ندارم.\n"
            "لطفاً مطمئن شوید ربات به عنوان ادمین کانال اضافه شده است."
        )
        return

    channel_id = channel.id

    state = await asyncio.to_thread(load_state)

    chat_state = get_chat_state(
        state,
        update.effective_chat.id,
    )

    channel_state = get_channel_state(
        chat_state,
        channel_id,
    )

    if action == "activate":

        channel_state["username"] = username
        channel_state["active"] = True

        await asyncio.to_thread(
            save_state,
            state,
        )

        context.user_data.pop("channel_action", None)

        await update.message.reply_text(
            "در صورت فعال بودن ربات در کانال، "
            "ارسال اخبار به صورت خودکار انجام خواهد شد. ✅"
        )

        await check_news(
            context.bot,
            update.effective_chat.id,
        )

        ensure_news_job(
            context,
            update.effective_chat.id,
        )

        return

    if action == "deactivate":

        reset_channel_state(
            chat_state,
            channel_id,
        )

        channel_state["username"] = username

        await asyncio.to_thread(
            save_state,
            state,
        )

        context.user_data.pop("channel_action", None)

        await update.message.reply_text(
            "ارسال اخبار برای این کانال متوقف و "
            "وضعیت اخبار آن ریست شد. 🔄"
        )


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