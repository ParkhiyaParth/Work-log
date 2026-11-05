import math
import os
import re
from functools import lru_cache

import requests

POSTCODE_RE = re.compile(r"\b([A-Z]{1,2}\d[A-Z\d]?)\s*(\d[A-Z]{2})\b")
HOURS_RE = re.compile(r"Hours/Week:\s*(\d{1,2})", re.I)
URL_RE = re.compile(r"https?://\S+")


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
    return geocode(os.getenv("HOME_POSTCODE", "HA1 3QH"))


def parse_post(text):
    m = POSTCODE_RE.search(text.upper())
    url = URL_RE.search(text)
    return {
        "postcode": f"{m.group(1)} {m.group(2)}" if m else None,
        "hours": [int(h) for h in HOURS_RE.findall(text)],
        "url": url.group(0).rstrip(").,") if url else None,
        "available": "no longer available" not in text.lower(),
    }


def evaluate(text):
    """Return (match, info dict incl. distance_miles)."""
    info = parse_post(text)
    info["distance_miles"] = None
    if not info["available"] or not info["hours"] or not info["postcode"]:
        return False, info
    if min(info["hours"]) > int(os.getenv("MAX_HOURS", "20")):
        return False, info
    job, me = geocode(info["postcode"]), home()
    if not job or not me:
        return False, info
    info["distance_miles"] = haversine_miles(*me, *job)
    return info["distance_miles"] <= float(os.getenv("RADIUS_MILES", "40")), info
