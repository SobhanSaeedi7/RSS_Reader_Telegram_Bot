import json
from pathlib import Path


STATE_FILE = Path("data/state.json")


def load_state():
    if not STATE_FILE.exists():
        return {"last_news_link": None}

    with STATE_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_state(last_news_link):
    state = {
        "last_news_link": last_news_link
    }

    with STATE_FILE.open("w", encoding="utf-8") as file:
        json.dump(state, file, ensure_ascii=False, indent=4)


