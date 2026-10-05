import os

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

from src.news_telegram_bot.rss import get_news, get_new_news
from src.news_telegram_bot.state import load_state, save_state
from src.news_telegram_bot.article import get_article_html, extract_article_text
from src.news_telegram_bot.llm import summary_chain


load_dotenv()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام! ربات خلاصه‌سازی اخبار ورزشی آماده است. 🏐"
    )


async def check_news(context: ContextTypes.DEFAULT_TYPE):
    print("\nChecking for new news...")

    # دریافت اخبار از RSS
    news = get_news()

    if not news:
        print("No news found.")
        return

    # خواندن state
    state = load_state()

    # پیدا کردن اخبار جدید
    new_news = get_new_news(
        news,
        state["last_news_link"]
    )

    if not new_news:
        print("No new news.")
        return

    print(f"Found {len(new_news)} new news.")

    # پردازش خبرهای جدید
    for item in reversed(new_news):
        print("\nProcessing:")
        print(item["title"])

        html = get_article_html(item["link"])

        article_text = extract_article_text(html)

        if article_text is None:
            print("Could not extract article text.")
            continue

        response = summary_chain.invoke({
            "article_text": article_text
        })

        print("\nSummary:")
        print(response.content)

        # فقط بعد از موفقیت پردازش، state را به‌روز می‌کنیم
        save_state(item["link"])


async def post_init(application: Application):
    await check_news(None)


def run_bot():
    token = os.getenv("TELEGRAM_BOT_TOKEN")

    application = (
        Application.builder()
        .token(token)
        .post_init(post_init)
        .build()
    )

    application.add_handler(CommandHandler("start", start))

    application.job_queue.run_repeating(
        check_news,
        interval=300,
    )

    application.run_polling()