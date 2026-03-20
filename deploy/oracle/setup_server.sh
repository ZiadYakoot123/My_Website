#!/usr/bin/env bash
set -euo pipefail

APP_DIR="/opt/my_website"
REPO_URL="https://github.com/ZiadYakoot123/My_Website.git"

sudo apt update
sudo apt install -y python3 python3-venv python3-pip git caddy

if [[ ! -d "$APP_DIR/.git" ]]; then
  sudo mkdir -p "$APP_DIR"
  sudo chown "$USER":"$USER" "$APP_DIR"
  git clone "$REPO_URL" "$APP_DIR"
else
  git -C "$APP_DIR" pull --ff-only
fi

cd "$APP_DIR"
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

if [[ ! -f .env ]]; then
  cat > .env << 'EOF'
FLASK_SECRET_KEY=replace-with-long-random-secret
ADMIN_USERNAME=admin
ADMIN_PASSWORD=replace-with-strong-password
DATABASE_PATH=/var/lib/my_website/database.db
EOF
fi

sudo mkdir -p /var/lib/my_website
sudo chown "$USER":www-data /var/lib/my_website
chmod 775 /var/lib/my_website

sudo cp deploy/oracle/mywebsite.service /etc/systemd/system/mywebsite.service
sudo cp deploy/oracle/Caddyfile /etc/caddy/Caddyfile

sudo systemctl daemon-reload
sudo systemctl enable --now mywebsite
sudo systemctl enable --now caddy

echo "Setup finished. Now point DNS A records for ziadyakoot.me and www to your VM public IP."
