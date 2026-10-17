#!/usr/bin/env bash
set -euo pipefail

APP_DIR="/opt/my_website"

cd "$APP_DIR"
git pull --ff-only
source .venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart mywebsite
sudo systemctl status mywebsite --no-pager -l
