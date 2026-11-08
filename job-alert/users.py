"""Users + their alert settings (SQLite). Each user gets a private ntfy topic and a secret edit link."""
import os
import secrets
import sqlite3

from filters import geocode

DB = os.getenv("APP_DB", "app.db")


def conn():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        secret TEXT PRIMARY KEY, topic TEXT UNIQUE, postcode TEXT, lat REAL, lon REAL,
        radius_miles REAL, min_hours INTEGER, max_hours INTEGER, min_pay REAL,
        alert_unknown_hours INTEGER, paused INTEGER DEFAULT 0, created INTEGER DEFAULT (strftime('%s','now')))""")
    return c


def clean(form):
    """Validate form input -> dict of settings. Raises ValueError with a friendly message."""
    import re
    pc = (form.get("postcode") or "").upper().strip()
    if not re.fullmatch(r"[A-Z]{1,2}\d[A-Z\d]?\s*\d[A-Z]{2}", pc):
        raise ValueError("Enter a full UK postcode, e.g. E1 6AN")
    ll = geocode(pc)
    if not ll:
        raise ValueError("We couldn't find that postcode")
    try:
        radius = float(form.get("radius_miles") or 30)
        mn = int(form.get("min_hours") or 0)
        mx = int(form.get("max_hours") or 20)
        pay = float(form.get("min_pay") or 0)
    except ValueError:
        raise ValueError("Numbers only please")
    if not (1 <= radius <= 200 and 0 <= mn <= mx <= 60 and 0 <= pay <= 100):
        raise ValueError("Those numbers look out of range")
    return dict(postcode=pc, lat=ll[0], lon=ll[1], radius_miles=radius, min_hours=mn, max_hours=mx,
                min_pay=pay, alert_unknown_hours=1 if form.get("alert_unknown_hours") else 0)


def create(form):
    d = clean(form)
    d["secret"], d["topic"] = secrets.token_urlsafe(16), "amzjob-" + secrets.token_hex(8)
    with conn() as c:
        c.execute("INSERT INTO users (secret,topic,postcode,lat,lon,radius_miles,min_hours,max_hours,min_pay,alert_unknown_hours)"
                  " VALUES (:secret,:topic,:postcode,:lat,:lon,:radius_miles,:min_hours,:max_hours,:min_pay,:alert_unknown_hours)", d)
    return d["secret"]


def get(secret):
    with conn() as c:
        r = c.execute("SELECT * FROM users WHERE secret=?", (secret,)).fetchone()
    return dict(r) if r else None


def update(secret, form):
    d = clean(form)
    d["secret"] = secret
    with conn() as c:
        c.execute("UPDATE users SET postcode=:postcode,lat=:lat,lon=:lon,radius_miles=:radius_miles,min_hours=:min_hours,"
                  "max_hours=:max_hours,min_pay=:min_pay,alert_unknown_hours=:alert_unknown_hours WHERE secret=:secret", d)


def set_paused(secret, paused):
    with conn() as c:
        c.execute("UPDATE users SET paused=? WHERE secret=?", (1 if paused else 0, secret))


def delete(secret):
    with conn() as c:
        c.execute("DELETE FROM users WHERE secret=?", (secret,))


def all_active():
    with conn() as c:
        return [dict(r) for r in c.execute("SELECT * FROM users WHERE paused=0")]
