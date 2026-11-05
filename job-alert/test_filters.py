from filters import evaluate

def post(pc, hrs, extra=""):
    return f"📍 X\n{pc}\n🕐 Hours/Week: {hrs}\n🔗 https://www.jobsatamazon.co.uk/app#/jobDetail?jobId=JOB-UK-1\n{extra}\n✅ Still Available"

def test_cases():
    assert evaluate(post("HA1 3QH", 20))[0]
    assert evaluate(post("RM13 9AA", 16))[0]          # east London
    assert evaluate(post("SL1 4AA", 20))[0]           # Slough
    assert not evaluate(post("HA1 3QH", 30))[0]       # too many hours
    assert not evaluate(post("PR26 6TZ", 20))[0]      # Preston, too far
    assert not evaluate(post("NR3 2BU", 20))[0]       # Norwich
    assert not evaluate(post("HA1 3QH", 20, "❌ No longer available"))[0]
    nohrs = "📍 Harrow HA1 3QH\n💼 Seasonal | Part-time\n🔗 https://x.co/j\n✅ Still Available"
    assert evaluate(nohrs)[0]                            # part-time, hours unlisted
    assert not evaluate(nohrs.replace("Part-time", "Full-time"))[0]
    m, i = evaluate(post("HA1 3QH", 40) + "\n🕐 Hours/Week: 20")  # multi-shift: any shift <= 20
    assert m
    print("ok", evaluate(post("CR0 4XY", 20))[1]["distance_miles"])

if __name__ == "__main__":
    test_cases()
