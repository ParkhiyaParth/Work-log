"""Server-side switch (no Telegram needed):  python testmode.py 10   |   python testmode.py off"""
import sys
import time

import settings

arg = sys.argv[1] if len(sys.argv) > 1 else "10"
until = 0 if arg == "off" else time.time() + int(arg) * 60
settings.save({"alert_all_until": until})
print("test mode OFF" if not until else f"test mode ON for {arg} min: every channel post will alert you")
