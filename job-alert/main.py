import asyncio
import os
import sqlite3
import time

from dotenv import load_dotenv
from telethon import TelegramClient, events
from telethon.sessions import StringSession

load_dotenv()
import commands  # noqa: E402
from filters import evaluate, home  # noqa: E402
from notify import push  # noqa: E402

db = sqlite3.connect("seen.db")
db.execute("CREATE TABLE IF NOT EXISTS seen (key TEXT PRIMARY KEY)")

channel = os.environ.get("TG_CHANNEL", "amazonukjobsalert")
channel = int(channel) if channel.lstrip("-").isdigit() else channel


def process(text):
    match, info = evaluate(text)
    if not match:
        return None
    key = f"{info['url']}|{info['hours']}|{text[:60]}"
    if db.execute("SELECT 1 FROM seen WHERE key=?", (key,)).fetchone():
        return None
    db.execute("INSERT INTO seen VALUES (?)", (key,))
    db.commit()
    return info


async def handler(event):  # new posts only; edits ("no longer available") are ignored
    t0 = time.time()
    text = event.raw_text or ""
    info = await asyncio.to_thread(process, text)
    if not info:
        return
    title = f"JOB {info['distance_miles']:.0f}mi: {min(info['hours'])}h/wk {info['postcode']}"
    await asyncio.to_thread(push, title, text[:400], info["url"])
    print(f"[ALERT] {title} sent in {time.time() - t0:.2f}s", flush=True)


async def my_commands(event):
    """Commands typed to yourself (Saved Messages) change the settings live."""
    reply = await asyncio.to_thread(commands.handle, event.raw_text)
    if reply:
        await event.reply(reply)
        print(f"[CMD] {event.raw_text!r}", flush=True)


async def main():
    print("Starting...", flush=True)
    await asyncio.to_thread(home)  # warm the geocode cache
    # Client MUST be created inside the running loop (otherwise it hangs after connecting).
    session = StringSession(os.environ["TG_SESSION"]) if os.getenv("TG_SESSION") else "session"
    client = TelegramClient(session, int(os.environ["TG_API_ID"]), os.environ["TG_API_HASH"])
    client.add_event_handler(handler, events.NewMessage(chats=channel))
    client.add_event_handler(my_commands, events.NewMessage(chats='me', from_users='me'))
    await client.connect()
    if not await client.is_user_authorized():
        raise SystemExit("Not logged in: TG_SESSION is missing or invalid")
    me = await client.get_me()
    print(f"Logged in as {me.first_name}. Listening on {channel}", flush=True)
    await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
