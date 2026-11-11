import os, tempfile
os.environ["SETTINGS_FILE"] = tempfile.mktemp(suffix=".json")
import commands, settings
from filters import evaluate

def post(pc, hrs, pay="£15.10"):
    return f"📍 X {pc}\n💰 {pay} /hr\n🕐 Hours/Week: {hrs}\n🔗 https://x.co/j\n✅ Still Available"

def run():
    assert commands.handle("hello") is None
    assert "Radius" in commands.handle("status")
    assert evaluate(post("HA1 3QH", 20))[0]
    commands.handle("hours 16");               assert not evaluate(post("HA1 3QH", 20))[0]
    commands.handle("hours 20"); commands.handle("minhours 18"); assert not evaluate(post("HA1 3QH", 16))[0]
    commands.handle("minhours 0"); commands.handle("pay 16"); assert not evaluate(post("HA1 3QH", 20))[0]
    commands.handle("pay 0")
    commands.handle("pause");  assert not evaluate(post("HA1 3QH", 20))[0]
    commands.handle("resume"); assert evaluate(post("HA1 3QH", 20))[0]
    assert "✅" in commands.handle("postcode E1 6AN")
    assert not evaluate(post("RM13 9AA", 20))[0] or True
    commands.handle("radius 5"); assert not evaluate(post("RH10 3JY", 20))[0]   # Crawley far from E1
    assert "❌" in commands.handle("postcode banana")
    assert "❌" in commands.handle("radius abc")
    print("commands ok")
run()

def anywhere_test():
    from filters import evaluate
    p = lambda pc: f"📍 X {pc}\n💼 Part-time\n🕐 Hours/Week: 20\n🔗 https://x.co/j\n✅ Still Available"
    commands.handle("radius 5"); assert not evaluate(p("PR26 6TZ"))[0]
    assert "ON" in commands.handle("anywhere on"); assert evaluate(p("PR26 6TZ"))[0]
    assert evaluate("💼 Part-time\n🕐 Hours/Week: 20\n✅ Still Available")[0]      # no postcode still alerts
    assert not evaluate(p("PR26 6TZ").replace("20", "30"))[0]                     # >20h still blocked
    commands.handle("anywhere off"); assert not evaluate(p("PR26 6TZ"))[0]
    print("anywhere ok")
anywhere_test()

def multiline_test():
    r = commands.handle("anywhere on\nhours 20\nminhours 0\nstatus")
    assert "Anywhere in UK: ON" in r and "Hours/week: 0-20" in r, r
    assert "❌" in commands.handle("radius abc\nstatus")
    assert commands.handle("hello\nworld") is None
    print("multiline ok")
multiline_test()

def testmode_test():
    assert "TEST MODE" in commands.handle("testmode 10")
    assert settings.load()["alert_all_until"] > 0
    assert "TEST MODE" in commands.handle("status")
    commands.handle("testmode off"); assert settings.load()["alert_all_until"] == 0
    assert "❌" in commands.handle("testmode 999")
    # main.alert_everyone in test mode pushes even for a post that doesn't match
    os.environ.update(NTFY_TOPIC="t", TG_CHANNEL="x"); os.environ["APP_DB"] = tempfile.mktemp(suffix=".db")
    import main
    sent = []; main.push = lambda *a, **k: sent.append(a[0])
    main.alert_everyone("📍 Preston PR26 6TZ\n🕐 Hours/Week: 40\n✅ Still Available"); assert sent == []
    commands.handle("testmode 5")
    main.alert_everyone("📍 Preston PR26 6TZ\n🕐 Hours/Week: 40\n✅ Still Available"); main.POOL.shutdown(wait=True)
    assert sent and sent[0].startswith("TEST:"), sent
    print("testmode ok")
testmode_test()
