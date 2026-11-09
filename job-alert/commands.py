"""Parse chat commands sent to yourself (Saved Messages) and update settings."""
import re

import settings
from filters import geocode

HELP = """Commands (send to Saved Messages):
postcode E1 6AN   - your location
radius 30         - max miles from you
hours 16          - max hours/week
minhours 10       - min hours/week
pay 15            - min £/hr (0 = off)
unknown on|off    - alert when hours not listed
anywhere on|off   - alert for jobs anywhere (ignore distance)
pause / resume    - stop/start alerts
status            - show settings
help              - this list"""


def status_text(s):
    return (f"Postcode: {s['postcode']}\nRadius: {s['radius_miles']:g} mi\n"
            f"Hours/week: {s['min_hours']}-{s['max_hours']}\nMin pay: £{s['min_pay']:g}/hr\n"
            f"Anywhere in UK: {'ON' if s['anywhere'] else 'off'}\n"
            f"Alert if hours unknown: {'on' if s['alert_unknown_hours'] else 'off'}\n"
            f"Alerts: {'PAUSED' if s['paused'] else 'on'}")


def handle(text):
    """Return a reply string if text is a command, else None."""
    t = (text or "").strip()
    m = re.match(r"^/?(postcode|radius|hours|minhours|pay|unknown|anywhere|pause|resume|status|help)\b\s*(.*)$", t, re.I)
    if not m:
        return None
    cmd, arg = m.group(1).lower(), m.group(2).strip()
    try:
        if cmd == "help":
            return HELP
        if cmd == "status":
            return status_text(settings.load())
        if cmd == "pause":
            return "⏸ Alerts paused.\n" + status_text(settings.save({"paused": True}))
        if cmd == "resume":
            return "▶️ Alerts on.\n" + status_text(settings.save({"paused": False}))
        if cmd == "postcode":
            pc = arg.upper()
            if not re.fullmatch(r"[A-Z]{1,2}\d[A-Z\d]?\s*\d[A-Z]{2}", pc) or not geocode(pc):
                return "❌ Not a valid UK postcode. Example: postcode E1 6AN"
            return "✅ Location updated.\n" + status_text(settings.save({"postcode": pc}))
        if cmd == "anywhere":
            if arg.lower() not in ("on", "off"):
                return "❌ Use: anywhere on  or  anywhere off"
            return "✅ Updated.\n" + status_text(settings.save({"anywhere": arg.lower() == "on"}))
        if cmd == "unknown":
            if arg.lower() not in ("on", "off"):
                return "❌ Use: unknown on  or  unknown off"
            return "✅ Updated.\n" + status_text(settings.save({"alert_unknown_hours": arg.lower() == "on"}))
        num = float(arg)
        if num < 0 or num > 1000:
            raise ValueError
        key = {"radius": "radius_miles", "hours": "max_hours", "minhours": "min_hours", "pay": "min_pay"}[cmd]
        val = num if cmd in ("radius", "pay") else int(num)
        return "✅ Updated.\n" + status_text(settings.save({key: val}))
    except ValueError:
        return f"❌ Couldn't read that. Example: {cmd} 20"
