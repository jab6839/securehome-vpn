from flask import Flask, render_template, request, redirect, url_for, session, flash, make_response
import subprocess
import datetime

app = Flask(__name__)
app.secret_key = 'securevpn'

# Toggle dark mode with cookies
@app.before_request
def set_dark_mode_cookie():
    if 'dark_mode' not in request.cookies:
        resp = make_response()
        resp.set_cookie('dark_mode', 'off')
        return resp

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'admin':
            session['username'] = username
            session['reminder'] = None
            return redirect(url_for('dashboard'))
        flash('Invalid credentials', 'error')
    return render_template('login.html')

@app.route('/logout', methods=['GET'])
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    dark_mode = request.cookies.get('dark_mode', 'off')
    return render_template('dashboard.html', username=session['username'], dark_mode=dark_mode)

@app.route('/toggle_dark_mode', methods=['POST'])
def toggle_dark_mode():
    current_mode = request.cookies.get('dark_mode', 'off')
    new_mode = 'on' if current_mode == 'off' else 'off'
    resp = make_response(redirect(url_for('dashboard')))
    resp.set_cookie('dark_mode', new_mode)
    return resp

@app.route('/connect_vpn', methods=['POST'])
def connect_vpn():
    flash('VPN connected successfully!', 'success')
    log_event("Connected")
    return redirect(url_for('dashboard'))

@app.route('/disconnect_vpn', methods=['POST'])
def disconnect_vpn():
    flash('VPN disconnected successfully!', 'success')
    log_event("Disconnected")
    return redirect(url_for('dashboard'))

@app.route('/set_reminder', methods=['POST'])
def set_reminder():
    reminder = request.form['reminder']
    session['reminder'] = reminder
    flash(f"Reminder set: {reminder}", 'info')
    return redirect(url_for('dashboard'))

@app.route('/set_server', methods=['POST'])
def set_server():
    server = request.form['server']
    flash(f"Server set to: {server}", 'info')
    return redirect(url_for('dashboard'))

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

def log_event(status):
    with open("vpn_logs.txt", "a") as file:
        file.write(f"{datetime.datetime.now()} - {status}\n")

if __name__ == '__main__':
    app.run(debug=True)

