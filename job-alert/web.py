"""Simple web app: enter your details, get alerts. Run: python web.py  (port 8000)."""
import html
import os

from flask import Flask, redirect, request

import users
from notify import push

app = Flask(__name__)
NTFY = os.getenv("NTFY_SERVER", "https://ntfy.sh")

CSS = """<meta name=viewport content="width=device-width,initial-scale=1"><style>
body{font-family:system-ui,sans-serif;margin:0;background:#f4f5f7;color:#111}
main{max-width:480px;margin:0 auto;padding:20px 16px 60px}h1{font-size:24px}
.card{background:#fff;border-radius:14px;padding:16px;margin:14px 0;box-shadow:0 1px 3px #0002}
label{display:block;margin:12px 0 4px;font-weight:600;font-size:14px}
input,select{width:100%;box-sizing:border-box;padding:12px;font-size:16px;border:1px solid #ccc;border-radius:10px}
button,.btn{display:block;width:100%;box-sizing:border-box;text-align:center;margin-top:14px;padding:14px;font-size:16px;
font-weight:700;border:0;border-radius:10px;background:#0b6bff;color:#fff;text-decoration:none}
.sec{background:#e8eaee;color:#111}.err{background:#ffe3e3;color:#900;padding:10px;border-radius:10px}
.row{display:flex;gap:10px}.row>div{flex:1}small{color:#555}code{background:#eee;padding:2px 5px;border-radius:5px;word-break:break-all}
</style>"""


def page(body):
    return f"<!doctype html><title>Job alerts</title>{CSS}<main>{body}</main>"


def form_body(u=None, err="", action="/signup", button="Start alerts", heading=True):
    u = u or {"postcode": "", "radius_miles": 30, "min_hours": 0, "max_hours": 20, "min_pay": 0, "alert_unknown_hours": 1}
    g = lambda k: html.escape(str(u[k]))
    return (f"""{'<h1>🔔 Warehouse job alerts</h1><p>Tell us what you want. We will send a loud alert the moment a matching job appears.</p>' if heading else ''}
{f'<p class=err>{html.escape(err)}</p>' if err else ''}
<form method=post action="{action}" class=card>
<label>Your postcode</label><input name=postcode value="{g('postcode')}" placeholder="e.g. HA1 3QH" autocapitalize=characters required>
<label>Max distance (miles)</label><input name=radius_miles type=number min=1 max=200 value="{g('radius_miles')}">
<div class=row><div><label>Min hours/week</label><input name=min_hours type=number min=0 max=60 value="{g('min_hours')}"></div>
<div><label>Max hours/week</label><input name=max_hours type=number min=0 max=60 value="{g('max_hours')}"></div></div>
<label>Minimum pay (£/hour, optional)</label><input name=min_pay type=number step=0.1 min=0 value="{g('min_pay')}">
<label><input type=checkbox name=alert_unknown_hours style="width:auto" {'checked' if u['alert_unknown_hours'] else ''}>
 Also alert part-time jobs that don't list hours</label>
<button>{button}</button></form>""")


def form(*a, **k):
    return page(form_body(*a, **k))


@app.get("/")
def home():
    return form()


@app.post("/signup")
def signup():
    try:
        return redirect(f"/u/{users.create(request.form)}")
    except ValueError as e:
        return form(err=str(e)), 400


@app.get("/u/<secret>")
def dashboard(secret):
    u = users.get(secret)
    if not u:
        return page("<h1>Not found</h1><p>This link isn't valid.</p>"), 404
    topic_url = f"{NTFY}/{u['topic']}"
    ntfy_link = f"ntfy://{NTFY.split('//')[1]}/{u['topic']}"
    status = "⏸ Paused" if u["paused"] else "✅ Alerts on"
    return page(f"""<h1>{status}</h1>
<div class=card><b>Step 1.</b> Install the free <b>ntfy</b> app (Android / iPhone).<br>
<b>Step 2.</b> Tap to subscribe to your private alerts:
<a class=btn href="{ntfy_link}">Subscribe in ntfy app</a>
<small>Or add the topic manually: <code>{u['topic']}</code></small><br><br>
<b>Step 3.</b> In ntfy set this topic to <b>Max priority</b> and allow it to override Do Not Disturb.
<form method=post action="/u/{secret}/test"><button class=sec>Send me a test alert</button></form></div>
<h2>Your settings</h2>{form_body(u, action=f"/u/{secret}/save", button="Save changes", heading=False)}
<div class=card><form method=post action="/u/{secret}/{'resume' if u['paused'] else 'pause'}">
<button class=sec>{'Resume alerts' if u['paused'] else 'Pause alerts'}</button></form>
<form method=post action="/u/{secret}/delete" onsubmit="return confirm('Delete your account?')"><button class=sec>Delete my account</button></form></div>
<p><small>Bookmark this page: this link is your login. Don't share it.</small></p>""")


@app.post("/u/<secret>/save")
def save(secret):
    if not users.get(secret):
        return page("<h1>Not found</h1>"), 404
    try:
        users.update(secret, request.form)
    except ValueError as e:
        return form(err=str(e), action=f"/u/{secret}/save", button="Save changes"), 400
    return redirect(f"/u/{secret}")


@app.post("/u/<secret>/test")
def test(secret):
    u = users.get(secret)
    if u:
        push("TEST: job alert", "If you hear this, alerts will reach you.", topic=u["topic"])
    return redirect(f"/u/{secret}")


@app.post("/u/<secret>/<action>")
def act(secret, action):
    if action in ("pause", "resume"):
        users.set_paused(secret, action == "pause")
        return redirect(f"/u/{secret}")
    if action == "delete":
        users.delete(secret)
        return redirect("/")
    return "", 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
