import asyncio
import os
import sqlite3
import time

from dotenv import load_dotenv
from telethon import TelegramClient, events
from telethon.sessions import StringSession

load_dotenv()
from filters import evaluate, home  # noqa: E402
from notify import push  # noqa: E402

db = sqlite3.connect("seen.db")
db.execute("CREATE TABLE IF NOT EXISTS seen (key TEXT PRIMARY KEY)")

# On a server set TG_SESSION (from make_session.py) so no login code is needed.
client = TelegramClient(StringSession(os.getenv("TG_SESSION", "")) if os.getenv("TG_SESSION") else "session",
                        int(os.environ["TG_API_ID"]), os.environ["TG_API_HASH"])
channel = os.environ.get("TG_CHANNEL", "amazonukjobsalert")
channel = int(channel) if channel.lstrip("-").isdigit() else channel


def process(text):
    match, info = evaluate(text)
    if not match:
        return None
    # Same job id + same shifts shouldn't re-alert within the same post text
    key = f"{info['url']}|{info['hours']}|{text[:60]}"
    if db.execute("SELECT 1 FROM seen WHERE key=?", (key,)).fetchone():
        return None
    db.execute("INSERT INTO seen VALUES (?)", (key,))
    db.commit()
    return info


@client.on(events.NewMessage(chats=channel))  # new posts only; edits ("no longer available") ignored
async def handler(event):
    t0 = time.time()
    text = event.raw_text or ""
    info = await asyncio.to_thread(process, text)
    if not info:
        return
    title = f"JOB {info['distance_miles']:.0f}mi: {min(info['hours'])}h/wk {info['postcode']}"
    await asyncio.to_thread(push, title, text[:400], info["url"])
    print(f"[ALERT] {title} sent in {time.time() - t0:.2f}s")


async def main():
    await asyncio.to_thread(home)  # warm the geocode cache
    await client.start()  # first run asks phone number + login code
    print("Listening on", channel)
    await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
