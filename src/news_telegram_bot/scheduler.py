from telegram.ext import ContextTypes

from news_telegram_bot.news_service import check_news


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


async def check_news_job(
    context: ContextTypes.DEFAULT_TYPE,
):
    await check_news(
        context.bot,
        context.job.chat_id,
    )