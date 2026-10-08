# 🏐 AI Sport News Telegram Bot

A Python-based Telegram bot that collects sports news from multiple Iranian sports news websites, extracts the full article content, summarizes each article using an LLM through **LangChain + AVAL AI**, and automatically sends the summaries to Telegram chats and channels.

---

## 📌 Overview

**AI Sport News Telegram Bot** is an automated sports-news aggregation and summarization system.

The bot currently collects news from:

* [Varzesh3](https://www.varzesh3.com/)
* [Khabar Varzeshi](https://www.khabarvarzeshi.com/)
* [Kayhan Varzeshi](https://kayhanvarzeshi.ir/)

For each news item, the bot:

1. Reads the RSS feed.
2. Detects new news.
3. Opens the original article.
4. Extracts the full article text.
5. Sends the article text to an LLM through LangChain.
6. Generates a short and accurate Persian summary.
7. Sends the summarized news and original link to Telegram.
8. Stores the latest processed news for each source to prevent duplicate messages.

The bot can work with:

* Private chats
* Groups
* Multiple Telegram channels

Each chat and channel maintains its **own independent news state**.

---

## ✨ Features

* 📰 Collect news from multiple RSS sources
* 🔎 Extract full article content from original news pages
* 🤖 AI-powered Persian news summarization
* 🧠 LangChain-based LLM pipeline
* 🔌 AVAL AI OpenAI-compatible API
* 📱 Telegram Bot integration
* 💬 Private chat support
* 👥 Group support
* 📢 Multiple Telegram channel support
* 🔄 Independent state for every chat and channel
* 🚫 Duplicate-news prevention
* ⏱️ Automatic news checking every 5 minutes
* 🛑 Start/stop news delivery with Telegram commands
* 🆘 Built-in `/help` command
* 🌱 Git branch-based development workflow
* ⚡ Dependency and environment management with `uv`

---


### Module responsibilities

| File              | Responsibility                                          |
| ----------------- | ------------------------------------------------------- |
| `rss.py`          | Fetch RSS feeds and detect new news                     |
| `article.py`      | Download and extract article text                       |
| `llm.py`          | Configure LangChain and AVAL AI summarization           |
| `state.py`        | Store independent state for chats and channels          |
| `telegram.py`     | Telegram bot, commands, scheduling and message delivery |
| `data/state.json` | Persistent news-tracking state                          |
| `.env`            | API keys and environment variables                      |
| `pyproject.toml`  | Project metadata and dependencies                       |
| `uv.lock`         | Exact locked dependency versions                        |

---



### News sources

The bot currently uses the following RSS feeds:

```text
Varzesh3
https://www.varzesh3.com/rss/all

Khabar Varzeshi
https://www.khabarvarzeshi.com/rss

Kayhan Varzeshi
https://kayhanvarzeshi.ir/fa/rss/allnews
```

---

# 📰 News Processing

## First activation

When a chat or channel is activated for the first time, there is no previous news state.

Therefore, the bot sends the **two latest news items from each source**.


---

## Subsequent checks

After the first execution, the bot stores the last processed news link for every source.


On the next check, the bot compares the RSS feed with the stored links.

Only news published after the last processed item is considered new.

This prevents the same news from being sent repeatedly.

---

# 🤖 Telegram Commands

The bot provides the following commands.

## `/start`

Activates news delivery for the current chat.

Example:

```text
/start
```

When `/start` is used:

1. The chat state is activated.
2. The bot checks for news immediately.
3. Initial news is sent if the chat has no previous state.
4. A scheduled job is created.
5. The bot continues checking for new news every 5 minutes.

### In groups

The bot can also be explicitly addressed:

```text
/start@Ai_Sport_News_Bot
```

This is useful when multiple bots are present in a group.

---

## `/reset`

Stops news delivery for the current chat and resets its news-tracking state.

```text
/reset
```

After reset:

```text
active = false
```

and the stored news links become:

```text
varzesh3 = null
khabarvarzeshi = null
kayhanvarzeshi = null
```

The scheduled job for that chat is also removed.

If `/start` is used again, the chat behaves like a newly activated chat and can receive the initial news set again.

---

## `/help`

Displays the available bot commands and explains how to use the bot.

```text
/help
```

The help command is intended to make the bot usable without requiring users to know the internal workflow.

---

# 📢 Telegram Channel Management

The bot supports sending news to Telegram channels.

A user does not need to configure a fixed channel ID in the source code.

Instead, channels can be activated dynamically.

---

## Step 1 — Add the bot to the channel

Add the bot as an administrator of the Telegram channel.

The bot must have permission to:

```text
Post Messages
```

Without this permission, the bot cannot send news to the channel.

---

## Step 2 — Activate a channel

In the bot's private chat, send:

```text
/active_on_channel
```

The bot will ask for the channel link.

Example:

```text
https://t.me/MySportsChannel
```

The bot then:

1. Finds the Telegram channel.
2. Retrieves its Telegram `chat_id`.
3. Creates an independent channel state.
4. Activates news delivery for that channel.
5. Performs an immediate news check.
6. Adds the channel to the scheduled checking workflow.

---

## Step 3 — Deactivate a channel

To stop sending news to a specific channel:

```text
/deactive_on_channel
```

The bot asks for the channel link.

After receiving the channel link:

* The channel is deactivated.
* Its news-tracking state is reset.
* No further news is sent to that channel.

---


# 🛠️ Installation

## Requirements


# ⚡ Installing `uv`

`uv` is used for Python environment management, dependency installation and project execution.

Official installation instructions are available on the [uv documentation](https://docs.astral.sh/uv/?utm_source=chatgpt.com).

### Windows

PowerShell:

```powershell
irm https://astral.sh/uv/install.ps1 | iex
```

After installation, verify:

```powershell
uv --version
```

You should see the installed `uv` version.

---

# 📥 Clone the Project

Clone the repository:

```bash
git clone https://github.com/SobhanSaeedi7/RSS_Reader_Telegram_Bot
```

Enter the project directory:

```bash
cd RSS_Reader_Telegram_Bot
```

---

# 🐍 Create the Environment and Install Dependencies

Because the project uses `uv`, the recommended setup is:

```bash
uv sync
```

`uv` will:

* Create the virtual environment if necessary.
* Install the project's dependencies.
* Use `pyproject.toml`.
* Respect the versions locked in `uv.lock`.

After this step, the project environment is ready.

---

# ▶️ Running the Project

The bot can be started through `uv`.

If the project exposes a dedicated entry point, use that entry point with:

```bash
uv run <ENTRY_POINT>
```

For the current project structure, the bot can also be started by calling `run_bot()` directly:

```bash
uv run python -c "from news_telegram_bot.telegram import run_bot; run_bot()"
```

Once started successfully, the process remains active and waits for Telegram updates.

Example:

```text
Application started
```

The terminal will remain running while the bot is active.

---

# 🧪 Basic Usage

After starting the application:

### Private Chat

Open the bot and send:

```text
/start
```

The bot activates itself for that chat and immediately checks the news.

Then use:

```text
/help
```

to view the available commands.

To stop and reset:

```text
/reset
```

---

# 👥 Using the Bot in a Group

Add the bot to a Telegram group.

Commands can be explicitly addressed to the bot:

```text
/start@Ai_Sport_News_Bot
```

and:

```text
/reset@Ai_Sport_News_Bot
```

The group receives its own independent state.

---

# 📢 Using the Bot with a Channel

1. Add the bot as a channel administrator.
2. Give it permission to post messages.
3. Open the bot's private chat.
4. Send:

```text
/active_on_channel
```

5. Send the channel link:

```text
https://t.me/YourChannel
```

6. The bot registers and activates that channel.

The channel will then receive the processed sports news automatically.

---

# 📰 Message Format

News messages are sent in the following general format:

```text
📰 Article Title

AI-generated summary of the article.

🔗 Original article link
```

The original source link is always included so the reader can access the complete article.

---

# 📁 Important Files

## `rss.py`

Responsible for:

* RSS source configuration
* Fetching RSS feeds
* Combining news from multiple sources
* Detecting new news

---

## `article.py`

Responsible for:

* Downloading article pages
* Parsing HTML
* Extracting article text
* Applying source-specific selectors

---

## `llm.py`

Responsible for:

* Loading the AVAL AI API key
* Configuring the LLM
* Creating the LangChain prompt
* Creating the summarization chain

---

## `state.py`

Responsible for:

* Loading persistent state
* Saving persistent state
* Creating chat state
* Creating channel state
* Resetting chat state
* Resetting channel state

---

## `telegram.py`

Responsible for:

* Telegram commands
* Starting and stopping news delivery
* Channel management
* Scheduled jobs
* Processing news
* Sending messages to Telegram

---



# 👨‍💻 Development

This project was developed as a practical learning project focused on:

* Python
* RSS
* Web scraping and HTML parsing
* APIs
* LangChain
* LLMs
* Telegram Bot API
* State management
* Async programming
* `uv`
* Git and GitHub
* Branch-based development
* Pull Requests

The project demonstrates how multiple independent technologies can be combined into an automated AI-powered news delivery pipeline.
