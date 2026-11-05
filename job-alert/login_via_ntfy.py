"""One-time headless Telegram login.
- Telegram sends a 5-digit code to your app; you publish it to your ntfy topic from your phone.
- The resulting session is encrypted and stored directly as the GitHub repo secret TG_SESSION.
- The session is never printed or sent to ntfy."""
import asyncio, base64, json, os, re, time

import requests
from nacl import encoding, public
from telethon import TelegramClient
from telethon.sessions import StringSession

SERVER = os.getenv("NTFY_SERVER", "https://ntfy.sh")
TOPIC = os.environ["NTFY_TOPIC"]
PHONE = os.environ["TG_PHONE"]
REPO = os.environ["GITHUB_REPOSITORY"]
GH = {"Authorization": f"Bearer {os.environ['GH_PAT']}", "Accept": "application/vnd.github+json"}


def say(title, body):
    requests.post(f"{SERVER}/{TOPIC}", data=body.encode(), headers={"Title": title, "Priority": "5"}, timeout=10)


def wait_for_code(since, minutes=10):
    end = time.time() + minutes * 60
    while time.time() < end:
        r = requests.get(f"{SERVER}/{TOPIC}/json?poll=1&since={since}", timeout=15)
        for line in r.text.splitlines():
            try:
                m = json.loads(line)
            except ValueError:
                continue
            text = (m.get("message") or "").strip()
            if m.get("event") == "message" and re.fullmatch(r"\d[\d\s\-]{3,6}\d", text):
                digits = re.sub(r"\D", "", text)
                if len(digits) == 5:
                    return digits
        time.sleep(3)
    raise SystemExit("timed out waiting for code")


def encrypt(public_key_b64, value):
    pk = public.PublicKey(public_key_b64.encode(), encoding.Base64Encoder())
    return base64.b64encode(public.SealedBox(pk).encrypt(value.encode())).decode()


def store_secret(name, value):
    k = requests.get(f"https://api.github.com/repos/{REPO}/actions/secrets/public-key", headers=GH, timeout=15)
    k.raise_for_status()
    k = k.json()
    r = requests.put(f"https://api.github.com/repos/{REPO}/actions/secrets/{name}", headers=GH, timeout=15,
                     json={"encrypted_value": encrypt(k["key"], value), "key_id": k["key_id"]})
    r.raise_for_status()


async def main():
    c = TelegramClient(StringSession(), int(os.environ["TG_API_ID"]), os.environ["TG_API_HASH"])
    await c.connect()
    sent = await c.send_code_request(PHONE)
    since = int(time.time())
    say("Telegram login", "Open Telegram, find the login code, then publish ONLY the 5 digits to this topic (within 10 min).")
    code = await asyncio.to_thread(wait_for_code, since)
    await c.sign_in(PHONE, code, phone_code_hash=sent.phone_code_hash)
    store_secret("TG_SESSION", c.session.save())
    say("Telegram login", "Done. TG_SESSION saved as a GitHub secret. You can now run the job-alert listener.")
    print("login ok; TG_SESSION stored as repo secret")
    await c.disconnect()

asyncio.run(main())
