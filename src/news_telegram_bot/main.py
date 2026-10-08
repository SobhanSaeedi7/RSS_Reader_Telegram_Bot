from news_telegram_bot.telegram import run_bot
from news_telegram_bot.state import reset_state


if __name__ == "__main__":
    try:
        run_bot()
    finally:
        reset_state()
        print("State reset.")