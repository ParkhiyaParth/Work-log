import asyncio
import os
import sqlite3
import time

from dotenv import load_dotenv
from telethon import TelegramClient, events
from telethon.sessions import StringSession

load_dotenv()
import commands  # noqa: E402
import users  # noqa: E402
from concurrent.futures import ThreadPoolExecutor  # noqa: E402
from filters import evaluate, home, match, parse_post  # noqa: E402
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


POOL = ThreadPoolExecutor(max_workers=16)


def alert_everyone(text):
    """Parse the post once, then alert every registered user whose settings match."""
    info = parse_post(text)
    import settings
    if os.getenv("NTFY_TOPIC") and settings.load().get("alert_all_until", 0) > time.time():
        # TEST MODE: alert for every channel post (auto-expires)
        first = (text.strip().splitlines() or [""])[0][:60]
        POOL.submit(push, f"TEST: {first}", text[:400], info["url"])
    if not info["available"]:
        return 0
    key = f"{info['url']}|{info['hours']}|{text[:60]}"
    if db.execute("SELECT 1 FROM seen WHERE key=?", (key,)).fetchone():
        return 0
    db.execute("INSERT INTO seen VALUES (?)", (key,))
    db.commit()
    sent = []
    for u in users.all_active():
        ok, miles = match(info, {**u, "alert_unknown_hours": bool(u["alert_unknown_hours"]), "anywhere": bool(u["anywhere"]), "paused": False}, (u["lat"], u["lon"]))
        if ok:
            where = f"{miles:.0f}mi" if miles is not None else "UK"
            title = f"JOB {where}: {min(info['hours']) if info['hours'] else '?'}h/wk {info['postcode'] or ''}"
            sent.append(POOL.submit(push, title, text[:400], info["url"], u["topic"]))
    # The owner (settings.json via Saved Messages commands) keeps alerting NTFY_TOPIC.
    if os.getenv("NTFY_TOPIC"):
        cfg = settings.load()
        ok, miles = match(info, cfg, home())
        if ok:
            where = f"{miles:.0f}mi" if miles is not None else "UK"
            title = f"JOB {where}: {min(info['hours']) if info['hours'] else '?'}h/wk {info['postcode'] or ''}".strip()
            sent.append(POOL.submit(push, title, text[:400], info["url"]))
    for f in sent:
        try:
            f.result(timeout=20)
        except Exception as e:  # one bad push must not block others
            print("[push error]", e, flush=True)
    return len(sent)


async def handler(event):  # new posts only; edits ("no longer available") are ignored
    t0 = time.time()
    n = await asyncio.to_thread(alert_everyone, event.raw_text or "")
    if n:
        print(f"[ALERT] {n} user(s) alerted in {time.time() - t0:.2f}s", flush=True)


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
