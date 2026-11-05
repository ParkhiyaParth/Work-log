import asyncio
import os
import sqlite3
import time

from dotenv import load_dotenv
from telethon import TelegramClient, events

load_dotenv()
from filters import first_url, is_match  # noqa: E402
from notify import push  # noqa: E402

db = sqlite3.connect("seen.db")
db.execute("CREATE TABLE IF NOT EXISTS seen (key TEXT PRIMARY KEY)")

client = TelegramClient("session", int(os.environ["TG_API_ID"]), os.environ["TG_API_HASH"])
channel = os.environ["TG_CHANNEL"]
channel = int(channel) if channel.lstrip("-").isdigit() else channel


@client.on(events.NewMessage(chats=channel))
async def handler(event):
    t0 = time.time()
    text = event.raw_text or ""
    print(f"[msg] {text[:80]!r}")
    if not is_match(text):
        return
    key = first_url(text) or text[:200]
    if db.execute("SELECT 1 FROM seen WHERE key=?", (key,)).fetchone():
        return
    db.execute("INSERT INTO seen VALUES (?)", (key,))
    db.commit()
    # run blocking HTTP off the event loop
    await asyncio.to_thread(push, "AMAZON JOB MATCH", text[:300], first_url(text))
    print(f"[ALERT] sent in {time.time() - t0:.2f}s")


async def main():
    await client.start()  # first run asks phone number + login code
    print("Listening on", channel)
    await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
