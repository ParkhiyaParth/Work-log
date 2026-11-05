from dotenv import load_dotenv
load_dotenv(".env.example")
from filters import is_match

def test_cases():
    assert is_match("Part time 16 hrs/week - Amazon Croydon CR0 4XY https://x.co/a")
    assert is_match("20 hours per week, London SE1 warehouse")
    assert not is_match("40 hours per week London E14")
    assert not is_match("Part time 16 hrs Manchester M1 1AA")
    assert is_match("Part time role at Dartford DA1")
    print("ok")

if __name__ == "__main__":
    test_cases()
