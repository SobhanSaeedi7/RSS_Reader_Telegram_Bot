import json
from pathlib import Path

STATE_FILE = Path("data/state.json")

SOURCES = [
    "varzesh3",
    "khabarvarzeshi",
    "kayhanvarzeshi",
]


def load_state():
    if not STATE_FILE.exists():
        return {"chats": {}}

    with STATE_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_state(state):
    with STATE_FILE.open("w", encoding="utf-8") as file:
        json.dump(
            state,
            file,
            ensure_ascii=False,
            indent=4,
        )


def get_chat_state(state, chat_id):
    chat_id = str(chat_id)

    if chat_id not in state["chats"]:
        state["chats"][chat_id] = {
            "last_news_links": {
                source: None
                for source in SOURCES
            },
            "active": False,
        }

    return state["chats"][chat_id]


def reset_chat_state(state, chat_id):
    chat_state = get_chat_state(state, chat_id)

    chat_state["last_news_links"] = {
        source: None
        for source in SOURCES
    }

    chat_state["active"] = False