"""Run ONCE anywhere (Codespace, Colab, PC). Logs in and prints TG_SESSION string."""
import os

from dotenv import load_dotenv
from telethon.sessions import StringSession
from telethon.sync import TelegramClient

load_dotenv()
api_id = int(os.getenv("TG_API_ID") or input("TG_API_ID: "))
api_hash = os.getenv("TG_API_HASH") or input("TG_API_HASH: ")
with TelegramClient(StringSession(), api_id, api_hash) as c:
    print("\nTG_SESSION (keep secret, add as a host secret):\n")
    print(c.session.save())
