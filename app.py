from flask import Flask, render_template, request, redirect, url_for, session, flash, make_response
import subprocess
import os
import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

WG_PATH = "/opt/homebrew/bin/wg"
WG_QUICK_PATH = "/opt/homebrew/bin/wg-quick"
CONFIG_PATH = "/Users/jadabrown/wireguard/wg0-client.conf"

# In-memory reminder (simple for now)
latest_reminder = ""

@app.route('/')
def home():
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'password':
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid credentials", 'error')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    vpn_status = check_vpn_status()
    theme = request.cookies.get('theme', 'light')
    return render_template(
        'dashboard.html',
        username=session['username'],
        vpn_status=vpn_status,
        reminder=latest_reminder,
        theme=theme
    )

@app.route('/connect', methods=['POST'])
def connect():
    try:
        subprocess.run(["sudo", WG_QUICK_PATH, "up", CONFIG_PATH], check=True)
        log_event("VPN Connected")
        flash("VPN Connected", 'success')
    except subprocess.CalledProcessError:
        log_event("VPN Connection Failed")
        flash("VPN Connection Failed", 'error')
    return redirect(url_for('dashboard'))

@app.route('/disconnect', methods=['POST'])
def disconnect():
    try:
        subprocess.run(["sudo", WG_QUICK_PATH, "down", CONFIG_PATH], check=True)
        log_event("VPN Disconnected")
        flash("VPN Disconnected", 'success')
    except subprocess.CalledProcessError:
        log_event("VPN Disconnection Failed")
        flash("VPN Disconnection Failed", 'error')
    return redirect(url_for('dashboard'))

@app.route('/set_server', methods=['POST'])
def set_server():
    server = request.form['server']
    flash(f"Server set to: {server}", 'info')
    return redirect(url_for('dashboard'))

@app.route('/set_reminder', methods=['POST'])
def set_reminder():
    global latest_reminder
    latest_reminder = request.form['reminder']
    flash("Reminder set successfully!", 'info')
    return redirect(url_for('dashboard'))

@app.route('/toggle_theme', methods=['POST'])
def toggle_theme():
    current = request.cookies.get('theme', 'light')
    new_theme = 'dark' if current == 'light' else 'light'
    resp = make_response(redirect(url_for('dashboard')))
    resp.set_cookie('theme', new_theme, max_age=60 * 60 * 24 * 30)  # 30 days
    return resp

@app.route('/launch_rustdesk', methods=['POST'])
def launch_rustdesk():
    try:
        subprocess.Popen(['open', '-a', 'RustDesk'])  # macOS
        flash("RustDesk launched.", 'success')
    except Exception as e:
        flash(f"Failed to launch RustDesk: {str(e)}", 'error')
    return redirect(url_for('dashboard'))

@app.route('/logs')
def logs():
    if 'username' not in session:
        return redirect(url_for('login'))
    try:
        with open('vpn_logs.txt', 'r') as f:
            log_entries = f.readlines()
    except FileNotFoundError:
        log_entries = []
    return render_template('logs.html', username=session['username'], logs=log_entries)

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

def log_event(status):
    with open("vpn_logs.txt", "a") as file:
        file.write(f"{datetime.datetime.now()} - {status}\n")

def check_vpn_status():
    try:
        output = subprocess.check_output([WG_PATH, 'show'], text=True)
        return 'Connected' if 'peer:' in output else 'Disconnected'
    except subprocess.CalledProcessError:
        return 'Disconnected'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

