import math
import os
import re
from functools import lru_cache

import requests

POSTCODE_RE = re.compile(r"\b([A-Z]{1,2}\d[A-Z\d]?)\s*(\d[A-Z]{2})\b")
HOURS_RE = re.compile(r"Hours/Week:\s*(\d{1,2})", re.I)
URL_RE = re.compile(r"https?://\S+")
PAY_RE = re.compile(r"£\s*(\d+(?:\.\d+)?)")


def haversine_miles(lat1, lon1, lat2, lon2):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 3958.8 * 2 * math.asin(math.sqrt(a))


@lru_cache(maxsize=2048)
def geocode(postcode):
    """(lat, lon) for a UK postcode via postcodes.io; falls back to outward code."""
    pc = postcode.replace(" ", "")
    for url in (f"https://api.postcodes.io/postcodes/{pc}",
                f"https://api.postcodes.io/outcodes/{pc[:-3]}"):
        try:
            r = requests.get(url, timeout=5)
            if r.ok:
                res = r.json()["result"]
                return res["latitude"], res["longitude"]
        except requests.RequestException:
            pass
    return None


def home():
    import settings
    return geocode(settings.load()["postcode"])


def parse_post(text):
    m = POSTCODE_RE.search(text.upper())
    url = URL_RE.search(text)
    return {
        "postcode": f"{m.group(1)} {m.group(2)}" if m else None,
        "hours": [int(h) for h in HOURS_RE.findall(text)],
        "url": url.group(0).rstrip(").,") if url else None,
        "part_time": bool(re.search(r"part[\s-]?time", text, re.I)),
        "available": "no longer available" not in text.lower(),
        "text": text,
    }


def match(info, cfg, me):
    """Does a parsed post fit one user's settings? me=(lat, lon). Returns (bool, miles)."""
    if cfg["paused"] or not info["available"] or not info["postcode"] or not me:
        return False, None
    if info["hours"]:
        if not any(cfg["min_hours"] <= h <= cfg["max_hours"] for h in info["hours"]):
            return False, None
    elif not (info["part_time"] and cfg["alert_unknown_hours"]):
        return False, None  # no hours listed: only alert if marked Part-time
    pay = PAY_RE.search(info.get("text", ""))
    if pay and float(pay.group(1)) < cfg["min_pay"]:
        return False, None
    job = geocode(info["postcode"])
    if not job:
        return False, None
    miles = haversine_miles(*me, *job)
    return miles <= cfg["radius_miles"], miles


def evaluate(text):
    """Single-user mode (settings.json). Return (match, info dict incl. distance_miles)."""
    import settings
    info = parse_post(text)
    info["text"] = text
    ok, miles = match(info, settings.load(), home())
    info["distance_miles"] = miles
    return ok, info
