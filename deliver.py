"""
deliver.py — sends the final digest message via Telegram.

SETUP (one-time):
1. On Telegram, search for "BotFather", send /newbot, follow prompts.
   You'll get a BOT TOKEN — put it in .env as TELEGRAM_BOT_TOKEN.
2. Search for your new bot by its username, open a chat, send it any message (e.g. "hi").
3. Run get_chat_id.py (below) to find your TELEGRAM_CHAT_ID, put it in .env.

Test sending directly:
    python deliver.py
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def send_telegram_message(text: str) -> bool:
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown",
    }
    resp = requests.post(url, json=payload, timeout=10)
    if resp.status_code == 200:
        print("Digest sent successfully.")
        return True
    else:
        print(f"Failed to send message: {resp.status_code} - {resp.text}")
        return False


if __name__ == "__main__":
    send_telegram_message("✅ Test message — your placement digest bot is connected!")
