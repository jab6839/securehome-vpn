# SecureHome VPN

SecureHome VPN is a lightweight, home-lab friendly dashboard for managing a WireGuard-based VPN and remote access (RustDesk). It shows live connection status, simple user management, and quick links/logs — all behind a small Flask app.

## Features
- 🛡️ WireGuard status & logs (read-only view)
- 💻 Optional RustDesk remote access link
- 📊 Clean dashboard UI (Jinja2 templates + CSS)
- 🧹 No heavy deps; easy to run on a Pi/mini PC
- 🔐 .env support (keep secrets out of code)

## Tech Stack
- Python 3, Flask, Jinja2
- HTML/CSS/JS
- (Optional) WireGuard, RustDesk on the host

## Quick Start
```bash
# clone
git clone https://github.com/jab6839/securehome-vpn.git
cd securehome-vpn

# create venv
python3 -m venv venv
source venv/bin/activate

# install deps
pip install -r requirements.txt  # if present; otherwise: pip install flask

# run
export FLASK_APP=app.py
flask run  # http://127.0.0.1:5000
