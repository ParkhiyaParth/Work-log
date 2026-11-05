# Amazon UK job alert

Listens to t.me/amazonukjobsalert, keeps jobs <=20 hrs/week within RADIUS_MILES of HOME_POSTCODE,
and sends a loud push with the apply link.

## Setup
1. `pip install -r requirements.txt`
2. Get `TG_API_ID`/`TG_API_HASH` at https://my.telegram.org. Copy `.env.example` to `.env` and fill in.
3. Install the **ntfy** app, subscribe to your long random topic. In the app set the topic to
   *Max priority* and allow it to override Do Not Disturb. (Optional: Pushover for repeat-until-acknowledged.)
4. `python main.py` (first run asks for your Telegram login code). Keep it running on a VPS/Pi: `nohup python main.py &` or systemd.
5. (Server) Run `bash install.sh` on an Ubuntu box to set up a systemd service.
6. Tune `HOME_POSTCODE`, `RADIUS_MILES`, `MAX_HOURS` in `.env`; test with `python test_filters.py`.

Tip: put the Amazon hiring site as a home-screen shortcut and stay logged in, so tapping the alert is the only step.
