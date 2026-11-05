import os
import re

HOURS_RE = re.compile(r"(\d{1,2})\s*(?:-\s*\d{1,2}\s*)?(?:hrs?|hours?|h)\b(?:\s*(?:/|per|a)\s*(?:week|wk))?", re.I)
PART_TIME_RE = re.compile(r"part[\s-]?time", re.I)
POSTCODE_RE = re.compile(r"\b([A-Z]{1,2})\d[A-Z\d]?\s*\d[A-Z]{2}\b|\b([A-Z]{1,2})\d[A-Z\d]?\b")
URL_RE = re.compile(r"https?://\S+")


def _csv(name):
    return [x.strip().lower() for x in os.getenv(name, "").split(",") if x.strip()]


def extract_hours(text):
    """Return list of weekly-hour numbers found in text."""
    return [int(m.group(1)) for m in HOURS_RE.finditer(text) if 1 <= int(m.group(1)) <= 60]


def hours_ok(text, max_hours):
    nums = extract_hours(text)
    if nums:
        return min(nums) <= max_hours
    # No number: accept explicit part-time wording
    return bool(PART_TIME_RE.search(text))


def location_ok(text):
    low = text.lower()
    if any(k in low for k in _csv("LOCATION_KEYWORDS")):
        return True
    prefixes = {p.upper() for p in _csv("POSTCODE_PREFIXES")}
    for m in POSTCODE_RE.finditer(text.upper()):
        area = m.group(1) or m.group(2)
        if area in prefixes:
            return True
    return False


def first_url(text):
    m = URL_RE.search(text)
    return m.group(0).rstrip(").,") if m else None


def is_match(text):
    max_hours = int(os.getenv("MAX_HOURS", "20"))
    return hours_ok(text, max_hours) and location_ok(text)
