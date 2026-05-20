#!/usr/bin/env python3
import http.server, sys, os, json, urllib.parse, uuid

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 7501
ROOM_DIR = os.path.dirname(os.path.abspath(__file__))
FLAG_REAL = "THM{cr0ss_s3rv1ce_r3us3}"
FLAG_FAKE = "THM{fake_web_dashboard}"
# بيانات اعتماد مُعاد استخدامها
WEB_ADMIN = {"username": "admin", "password": "MyS3cr3tP@ss"}  # نفسها لـ SSH وDB
comments_store = []

LOGIN_PAGE = """<!DOCTYPE html>
<html><head><title>Internal Portal</title>
<style>body{background:#0a0c10;display:flex;justify-content:center;align-items:center;height:100vh;font-family:'Segoe UI',sans-serif;}
.box{background:#1a1c2b;padding:2rem;border-radius:12px;} h2{color:#e53170;}
input{width:100%;padding:10px;margin:8px 0;background:#0d0f1a;border:1px solid #333;color:white;border-radius:5px;}
input[type=submit]{background:#e53170;border:none;cursor:pointer;font-weight:bold;}
</style></head><body><div class="box"><h2>Employee Portal</h2>
<form method="POST" action="/login"><input name="username" placeholder="Username"><br>
<input type="password" name="password" placeholder="Password"><br>
<input type="submit" value="Log In"></form>
<!-- Default admin account: admin / MyS3cr3tP@ss -->
</div></body></html>"""

DASHBOARD = """<!DOCTYPE html>
<html><head><title>Dashboard</title>
<style>body{background:#0a0c10;color:#c9d1d9;font-family:'Segoe UI',sans-serif;padding:2rem;}
h2{color:#00ff00;} .card{background:#1a1c2b;padding:1rem;border-radius:8px;margin:1rem 0;}
textarea,input{width:100%;padding:10px;margin:5px 0;background:#0d0f1a;border:1px solid #333;color:white;border-radius:5px;}
button{background:#00aa00;border:none;padding:10px 20px;color:white;font-weight:bold;cursor:pointer;}
.comment{background:#111;margin:10px 0;padding:10px;border-radius:5px;}</style></head><body>
<h2>Employee Dashboard</h2>
<div class="card">
<h3>System Notes</h3>
<p>SSH server: localhost:7502 (user: admin, pass: same as web)</p>
<p>Database server: localhost:7503 (user: admin, pass: same as web)</p>
<p>Flag (debug only): {fake_flag}</p>
</div>
<div class="card">
<h3>Comments</h3>
<form method="POST" action="/comment"><textarea name="comment" placeholder="Leave a comment"></textarea><br>
<button>Post</button></form>
<div>%COMMENTS%</div>
</div>
<a href="/logout" style="color:#e53170;">Logout</a></body></html>"""

sessions = {}

class WebHandler(http.server.BaseHTTPRequestHandler):
    def handle_one_request(self):
        try:
            super().handle_one_request()
        except (ConnectionResetError, BrokenPipeError):
            pass

    def do_GET(self):
        if self.path == "/":
            self._serve_html(LOGIN_PAGE)
        elif self.path == "/dashboard":
            if not self._is_auth():
                self.send_error(403); return
            comments_html = "".join(f'<div class="comment">{c}</div>' for c in comments_store)
            page = DASHBOARD.replace("{fake_flag}", FLAG_FAKE).replace("%COMMENTS%", comments_html)
            self._serve_html(page)
        elif self.path == "/logout":
            self._clear_auth()
            self.send_response(302)
            self.send_header("Location", "/")
            self.end_headers()
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path == "/login":
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode()
            data = urllib.parse.parse_qs(body)
            user = data.get('username', [''])[0]
            pwd = data.get('password', [''])[0]
            if user == WEB_ADMIN["username"] and pwd == WEB_ADMIN["password"]:
                sid = uuid.uuid4().hex
                sessions[sid] = user
                self.send_response(302)
                self.send_header("Set-Cookie", f"session={sid}; Path=/")
                self.send_header("Location", "/dashboard")
                self.end_headers()
            else:
                self.send_error(403, "Invalid credentials")
        elif self.path == "/comment":
            if not self._is_auth():
                self.send_error(403); return
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode()
            data = urllib.parse.parse_qs(body)
            comment = data.get('comment', [''])[0]
            # Stored XSS: no sanitization
            comments_store.append(comment)
            self.send_response(302)
            self.send_header("Location", "/dashboard")
            self.end_headers()
        else:
            self.send_error(404)

    def _is_auth(self):
        cookie = self.headers.get('Cookie', '')
        if 'session=' in cookie:
            sid = cookie.split('session=')[1].split(';')[0]
            return sid in sessions
        return False

    def _clear_auth(self):
        self.send_header("Set-Cookie", "session=; expires=Thu, 01 Jan 1970 00:00:00 GMT")

    def _serve_html(self, html):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode())

    def log_message(self, format, *args):
        pass

if __name__ == "__main__":
    server = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), WebHandler)
    print("Web active", flush=True)
    server.serve_forever()
