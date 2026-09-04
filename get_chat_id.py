"""
get_chat_id.py — one-time helper to find your TELEGRAM_CHAT_ID.

Steps:
1. Message your bot anything on Telegram first (e.g. "hi").
2. Put your TELEGRAM_BOT_TOKEN in .env
3. Run: python get_chat_id.py
4. Copy the chat id it prints into .env as TELEGRAM_CHAT_ID
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

resp = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates", timeout=10)
data = resp.json()

if not data.get("result"):
    print("No messages found. Make sure you messaged your bot first, then re-run this.")
else:
    for update in data["result"]:
        chat = update["message"]["chat"]
        print(f"Found chat — id: {chat['id']}, name: {chat.get('first_name', 'Unknown')}")
