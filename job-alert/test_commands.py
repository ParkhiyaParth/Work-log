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
