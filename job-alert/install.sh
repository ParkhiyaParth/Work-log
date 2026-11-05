#!/usr/bin/env bash
# One-shot setup for Ubuntu/Debian (e.g. Oracle Cloud). Run from inside job-alert/:  bash install.sh
set -euo pipefail
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

sudo apt-get update -y && sudo apt-get install -y python3 python3-venv python3-pip git
python3 -m venv .venv
.venv/bin/pip install -q --upgrade pip setuptools wheel
.venv/bin/pip install -q -r requirements.txt

if [ ! -f .env ]; then
  cp .env.example .env
  echo ">> Created .env. Edit it now:  nano $DIR/.env   (set TG_API_ID, TG_API_HASH, NTFY_TOPIC)"
  echo ">> Then run this script again."; exit 0
fi

if ! grep -q '^TG_SESSION=.\+' .env; then
  echo ">> Telegram login (one time). Enter phone +44..., then the code Telegram sends you."
  SESSION=$(.venv/bin/python make_session.py | tail -n 1)
  echo "TG_SESSION=$SESSION" >> .env
  chmod 600 .env
fi

sudo tee /etc/systemd/system/job-alert.service >/dev/null <<UNIT
[Unit]
Description=Amazon UK job alert
After=network-online.target
Wants=network-online.target

[Service]
User=$USER
WorkingDirectory=$DIR
ExecStart=$DIR/.venv/bin/python -u main.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
UNIT
sudo systemctl daemon-reload
sudo systemctl enable --now job-alert
sleep 3
sudo systemctl --no-pager status job-alert | head -n 12
echo ">> Live logs:  journalctl -u job-alert -f"
