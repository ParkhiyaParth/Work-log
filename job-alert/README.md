# Amazon UK job alert

Listens to a Telegram channel, filters for <=20 hrs/week jobs in London/border areas,
and sends a loud push notification to your phone with the apply link.

## Setup
1. `pip install -r requirements.txt`
2. Get `TG_API_ID`/`TG_API_HASH` at https://my.telegram.org. Copy `.env.example` to `.env` and fill in.
3. Install the **ntfy** app, subscribe to your long random topic. In the app set the topic to
   *Max priority* and allow it to override Do Not Disturb. (Optional: Pushover for repeat-until-acknowledged.)
4. `python main.py` (first run asks for your Telegram login code). Keep it running on a VPS/Pi: `nohup python main.py &` or systemd.
5. Tune filters in `.env`; test with `python test_filters.py`.

Tip: put the Amazon hiring site as a home-screen shortcut and stay logged in, so tapping the alert is the only step.
