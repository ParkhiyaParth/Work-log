#!/usr/bin/env bash
# Usage: TG_API_ID=.. TG_API_HASH=.. NTFY_TOPIC=.. bash <(curl -fsSL <raw url>/bootstrap.sh)
set -euo pipefail
if command -v apt-get >/dev/null; then sudo apt-get update -y && sudo apt-get install -y git; else sudo dnf install -y git; fi
[ -d work-log ] || git clone -b ccr-24d468f0-3ut1j8 https://github.com/parkhiyaparth/work-log
cd work-log && git pull -q origin ccr-24d468f0-3ut1j8
cd job-alert && bash install.sh
