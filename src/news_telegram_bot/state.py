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
        state = json.load(file)

    state.setdefault("chats", {})

    return state


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
            "channels": {},
        }


    state["chats"][chat_id].setdefault(
        "channels",
        {},
    )

    return state["chats"][chat_id]


def get_channel_state(chat_state, channel_id):
    channel_id = str(channel_id)

    if channel_id not in chat_state["channels"]:
        chat_state["channels"][channel_id] = {
            "username": None,
            "active": False,
            "last_news_links": {
                source: None
                for source in SOURCES
            },
        }

    return chat_state["channels"][channel_id]


def reset_chat_state(state, chat_id):
    chat_state = get_chat_state(state, chat_id)

    chat_state["last_news_links"] = {
        source: None
        for source in SOURCES
    }

    chat_state["active"] = False


def reset_channel_state(chat_state, channel_id):
    channel_state = get_channel_state(
        chat_state,
        channel_id,
    )

    channel_state["last_news_links"] = {
        source: None
        for source in SOURCES
    }

    channel_state["active"] = False