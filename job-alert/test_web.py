import os, tempfile
os.environ["APP_DB"] = tempfile.mktemp(suffix=".db")
import users, web
from filters import parse_post, match

c = web.app.test_client()
assert b"Warehouse job alerts" in c.get("/").data
r = c.post("/signup", data={"postcode": "banana"}); assert r.status_code == 400
r = c.post("/signup", data={"postcode": "HA1 3QH", "radius_miles": "40", "max_hours": "20"}); assert r.status_code == 302
secret = r.headers["Location"].split("/u/")[1]
assert b"Alerts on" in c.get(f"/u/{secret}").data
u = users.get(secret)
job = lambda pc, h: parse_post(f"📍 {pc}\n💼 Part-time\n💰 £15.10 /hr\n🕐 Hours/Week: {h}\n🔗 https://x.co/j\n✅ Still Available")
cfg = {**u, "alert_unknown_hours": True, "paused": False}
assert match(job("HA1 3QH", 20), cfg, (u["lat"], u["lon"]))[0]
assert not match(job("PR26 6TZ", 20), cfg, (u["lat"], u["lon"]))[0]
c.post(f"/u/{secret}/save", data={"postcode": "E1 6AN", "radius_miles": "5", "max_hours": "16"})
assert users.get(secret)["postcode"] == "E1 6AN"
c.post(f"/u/{secret}/pause"); assert users.all_active() == []
c.post(f"/u/{secret}/resume"); assert len(users.all_active()) == 1
c.post(f"/u/{secret}/delete"); assert users.get(secret) is None
print("web ok")
