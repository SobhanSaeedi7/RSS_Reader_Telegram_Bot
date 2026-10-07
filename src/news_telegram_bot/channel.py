import asyncio

from telegram import Update
from telegram.ext import ContextTypes

from news_telegram_bot.news_service import check_news
from news_telegram_bot.scheduler import ensure_news_job
from news_telegram_bot.state import (
    load_state,
    save_state,
    get_chat_state,
    get_channel_state,
    reset_channel_state,
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

        context.user_data.pop(
            "channel_action",
            None,
        )

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

        context.user_data.pop(
            "channel_action",
            None,
        )

        await update.message.reply_text(
            "ارسال اخبار برای این کانال متوقف و "
            "وضعیت اخبار آن ریست شد. 🔄"
        )