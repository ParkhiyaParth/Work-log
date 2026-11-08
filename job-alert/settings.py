"""Live-editable settings, stored in settings.json (defaults come from .env)."""
import json
import os
import threading

PATH = os.getenv("SETTINGS_FILE", "settings.json")
_lock = threading.Lock()


def _defaults():
    return {
        "postcode": os.getenv("HOME_POSTCODE", "HA1 3QH"),
        "max_hours": int(os.getenv("MAX_HOURS", "20")),
        "min_hours": int(os.getenv("MIN_HOURS", "0")),
        "radius_miles": float(os.getenv("RADIUS_MILES", "40")),
        "min_pay": float(os.getenv("MIN_PAY", "0")),
        "alert_unknown_hours": os.getenv("ALERT_UNKNOWN_HOURS", "1") == "1",
        "paused": False,
    }


def load():
    s = _defaults()
    try:
        with open(PATH) as f:
            s.update(json.load(f))
    except (OSError, ValueError):
        pass
    return s


def save(updates):
    with _lock:
        s = load()
        s.update(updates)
        with open(PATH, "w") as f:
            json.dump(s, f, indent=2)
        return s
