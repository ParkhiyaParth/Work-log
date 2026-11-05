import os
import requests


def push(title, body, url=None):
    """Send loud push via ntfy (urgent) and/or Pushover (emergency)."""
    sent = False
    topic = os.getenv("NTFY_TOPIC")
    if topic:
        headers = {"Title": title, "Priority": "5", "Tags": "rotating_light,briefcase"}
        if url:
            headers["Click"] = url
            headers["Actions"] = f"view, Apply now, {url}"
        requests.post(f"{os.getenv('NTFY_SERVER', 'https://ntfy.sh')}/{topic}",
                      data=body.encode("utf-8"), headers=headers, timeout=10)
        sent = True
    user, token = os.getenv("PUSHOVER_USER"), os.getenv("PUSHOVER_TOKEN")
    if user and token:
        data = {"user": user, "token": token, "title": title, "message": body,
                "priority": 2, "retry": 30, "expire": 600}  # repeats until acknowledged
        if url:
            data.update(url=url, url_title="Apply now")
        requests.post("https://api.pushover.net/1/messages.json", data=data, timeout=10)
        sent = True
    if not sent:
        print("!! No push provider configured (set NTFY_TOPIC or PUSHOVER_*)")
