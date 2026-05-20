#!/usr/bin/env python3
import sys, time, threading, uuid, http.server
from urllib.parse import parse_qs, urlparse

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 6085
FLAG = "THM{r4ce_c0nd1t10n_byp4ss}"
FAKE_FLAG = "THM{fake_flag_race}"  # للخداع

# قاعدة مستخدمين وهمية
USERS = {"admin": "admin123", "user": "password"}

# جلسات: session_id -> username
sessions = {}
sessions_lock = threading.Lock()

LOGIN_HTML = """<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><title>High‑Security Login</title>
<style>
    body{background:#0b0d17;color:#e6e6e6;font-family:'Segoe UI',sans-serif;display:flex;justify-content:center;align-items:center;height:100vh;margin:0;}
    .box{background:#1a1c2b;padding:2rem;border-radius:12px;box-shadow:0 0 20px rgba(0,255,255,0.2);}
    h2{color:#00ffff;} input{width:100%;padding:10px;margin:8px 0;border:1px solid #333;background:#0d0f1a;color:white;border-radius:5px;}
    input[type=submit]{background:#00aaaa;border:none;font-weight:bold;cursor:pointer;}
    input[type=submit]:hover{background:#008888;}
</style></head>
<body><div class="box"><h2>Restricted Login</h2>
<form method="POST" action="/login">
<input name="username" placeholder="Username"><br>
<input type="password" name="password" placeholder="Password"><br>
<input type="submit" value="Sign In">
</form>
<!-- TODO: remove timing debug in production -->
</div></body></html>"""

DASHBOARD = """<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><title>Dashboard</title>
<style>
    body{background:#0b0d17;color:#e6e6e6;font-family:'Segoe UI',sans-serif;padding:2rem;}
    h2{color:#00ffff;} .card{background:#1a1c2b;padding:1.5rem;border-radius:8px;margin:1rem 0;}
</style></head>
<body>
<h2>Welcome, {user}</h2>
<div class="card">
    <p>Your flag: <strong>{flag}</strong></p>
</div>
<a href="/logout" style="color:#ff5555;">Logout</a>
</body></html>"""

DEV_NOTES = """Development Notes
- Login system uses multi‑threaded server (ThreadingTCPServer)
- Added 0.5s delay after password verification (debugging purposes)
- Race condition possible? Look at timing...
- Admin creds: admin / admin123
"""

ROBOTS_TXT = """User-agent: *
Disallow: /dev-notes.txt
Disallow: /fake-admin
"""

FAKE_ADMIN_HTML = """<html><body><h1>Admin Panel</h1><p>Flag: """ + FAKE_FLAG + """</p></body></html>"""

class RaceHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        if path == "/":
            self._serve_html(LOGIN_HTML)
        elif path == "/robots.txt":
            self._serve_text(ROBOTS_TXT)
        elif path == "/dev-notes.txt":
            self._serve_text(DEV_NOTES)
        elif path == "/fake-admin":
            self._serve_html(FAKE_ADMIN_HTML)
        elif path == "/dashboard":
            username = self._get_session_user()
            if username:
                flag_to_show = FLAG if username == "admin" else FAKE_FLAG
                page = DASHBOARD.replace("{user}", username).replace("{flag}", flag_to_show)
                self._serve_html(page)
            else:
                self.send_error(403, "Not authenticated")
        elif path == "/logout":
            sess_id = self._get_cookie("session")
            if sess_id:
                with sessions_lock:
                    sessions.pop(sess_id, None)
            self.send_response(302)
            self.send_header("Location", "/")
            self.end_headers()
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path == "/login":
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode()
            data = parse_qs(body)
            username = data.get('username', [''])[0]
            password = data.get('password', [''])[0]

            # Authentication check
            if username in USERS and USERS[username] == password:
                # ***** RACE WINDOW: small delay before session creation *****
                time.sleep(0.5)  # artificial delay to make race practical
                sess_id = str(uuid.uuid4())
                with sessions_lock:
                    sessions[sess_id] = username
                self.send_response(302)
                self.send_header("Set-Cookie", f"session={sess_id}; Path=/")
                self.send_header("Location", "/dashboard")
                self.end_headers()
            else:
                # Delay also for failed logins? No, but we still mimic small delay
                self.send_response(302)
                self.send_header("Location", "/")
                self.end_headers()
        else:
            self.send_error(404)

    def _get_cookie(self, key):
        cookie_str = self.headers.get('Cookie', '')
        for part in cookie_str.split(';'):
            part = part.strip()
            if part.startswith(f'{key}='):
                return part[len(key)+1:]
        return None

    def _get_session_user(self):
        sess_id = self._get_cookie('session')
        if not sess_id:
            return None
        with sessions_lock:
            return sessions.get(sess_id)

    def _serve_html(self, html):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode())

    def _serve_text(self, text):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(text.encode())

    def log_message(self, format, *args):
        pass

if __name__ == "__main__":
    server = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), RaceHandler)
    print(f"Race server running on http://127.0.0.1:{PORT}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
