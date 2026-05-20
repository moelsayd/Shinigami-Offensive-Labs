#!/usr/bin/env python3
import http.server, sys, json, base64, hmac, hashlib, os, urllib.parse, time, uuid, sqlite3, threading

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8101
ROOM_DIR = os.path.dirname(os.path.abspath(__file__))
SECRET = b"supersecretkey123"  # تم تسريبه في robots.txt و debug
FLAG_FAKE = "THM{fake_web_portal}"
DB_PATH = os.path.join(ROOM_DIR, "pivot.db")

# إعداد قاعدة البيانات
conn = sqlite3.connect(DB_PATH)
conn.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, role TEXT, token_data TEXT)")
conn.execute("INSERT OR IGNORE INTO users VALUES (1, 'admin', 'admin', '{\"role\":\"admin\",\"ssh_hint\":\"developer:dev123\"}')")
conn.execute("INSERT OR IGNORE INTO users VALUES (2, 'guest', 'user', '{}')")
conn.commit()
conn.close()

# ---------- JWT Mini-lib ----------
def b64e(d): return base64.urlsafe_b64encode(d).rstrip(b'=').decode()
def b64d(d):
    d += '=' * (4 - len(d) % 4)
    return base64.urlsafe_b64decode(d)
def jwt_create(payload, secret=SECRET, alg="HS256"):
    header = {"alg":alg,"typ":"JWT"}
    h = b64e(json.dumps(header).encode())
    p = b64e(json.dumps(payload).encode())
    if alg == "none":
        return f"{h}.{p}."
    sig = b64e(hmac.new(secret, f"{h}.{p}".encode(), hashlib.sha256).digest())
    return f"{h}.{p}.{sig}"
def jwt_verify(token):
    try:
        h, p, sig = token.split(".")
        header = json.loads(b64d(h))
        alg = header.get("alg","HS256")
        if alg == "none":
            return json.loads(b64d(p))
        expected = b64e(hmac.new(SECRET, f"{h}.{p}".encode(), hashlib.sha256).digest())
        if sig != expected:
            return None
        return json.loads(b64d(p))
    except:
        return None

# ---------- HTML Templates ----------
LOGIN_PAGE = """<!DOCTYPE html>
<html><head><title>TruePivot Portal</title>
<style>body{background:#0a0c10;display:flex;justify-content:center;align-items:center;height:100vh;font-family:'Segoe UI',sans-serif;}
.box{background:#1a1c2b;padding:2rem;border-radius:12px;} h2{color:#e53170;}
input{width:100%;padding:10px;margin:8px 0;background:#0d0f1a;border:1px solid #333;color:white;border-radius:5px;}
input[type=submit]{background:#e53170;border:none;cursor:pointer;}
</style></head><body><div class="box"><h2>Employee Portal</h2>
<form method="POST" action="/login"><input name="username" placeholder="Username"><br>
<input type="password" name="password" placeholder="Password"><br>
<input type="submit" value="Log In"></form>
</div></body></html>"""

DASHBOARD = """<html><head><title>Dashboard</title>
<style>body{background:#0a0c10;color:#c9d1d9;font-family:'Segoe UI',sans-serif;padding:2rem;}
h2{color:#00ff00;} .card{background:#1a1c2b;padding:1rem;border-radius:8px;margin:1rem 0;}
a{color:#58a6ff;}</style></head><body>
<h2>Dashboard</h2><div class="card"><p>Flag: {flag}</p></div>
<a href="/admin/metrics">Internal Metrics (admin only)</a><br><a href="/logout">Logout</a></body></html>"""

METRICS_PAGE = """<html><head><title>Metrics</title>
<style>body{background:#0a0c10;color:#c9d1d9;font-family:'Segoe UI',sans-serif;padding:2rem;}
input,button{padding:8px;border-radius:5px;margin:5px;} input{background:#0d0f1a;border:1px solid #333;color:white;}
button{background:#00aa00;border:none;color:white;font-weight:bold;cursor:pointer;}</style></head><body>
<h2>Internal Metrics</h2><div class="card">
<p>Lookup user by ID (id=1,2,...)</p>
<form method="GET" action="/admin/metrics"><input name="id" placeholder="ID"><button>Search</button></form>
<div style="background:#0d0f1a;padding:1rem;margin-top:1rem;border-radius:5px;">%RESULT%</div>
</div><a href="/dashboard">Back</a></body></html>"""

ROBOTS_TXT = "User-agent: *\nDisallow: /debug\nInternal note: JWT secret is 'supersecretkey123'"

DEBUG = json.dumps({"status":"debug","jwt_secret":"supersecretkey123"})

sessions = {}

class PivotHandler(http.server.BaseHTTPRequestHandler):
    def handle_one_request(self):
        try:
            super().handle_one_request()
        except (ConnectionResetError, BrokenPipeError):
            pass

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        qs = urllib.parse.parse_qs(parsed.query)
        token = self._get_token()

        if path == "/":
            self._serve_html(LOGIN_PAGE)
        elif path == "/robots.txt":
            self._serve_text(ROBOTS_TXT)
        elif path == "/debug":
            self._serve_json(DEBUG)
        elif path == "/dashboard":
            payload = jwt_verify(token) if token else None
            if not payload:
                self.send_error(403); return
            flag_shown = FLAG_FAKE if payload.get("role")!="admin" else "Access granted. Check /admin/metrics."
            self._serve_html(DASHBOARD.replace("{flag}", flag_shown))
        elif path == "/admin/metrics":
            payload = jwt_verify(token) if token else None
            if not payload or payload.get("role")!="admin":
                self.send_error(403); return
            uid = qs.get('id', [None])[0]
            if uid:
                conn = sqlite3.connect(DB_PATH)
                try:
                    # Time-Based Blind SQLi: إذا كان المستخدم موجوداً يضيف تأخيراً
                    query = f"SELECT 1 FROM users WHERE id = {uid}"
                    start = time.time()
                    row = conn.execute(query).fetchone()
                    if row:
                        time.sleep(2)  # تأخير مرئي للكشف
                        result = "User exists"
                    else:
                        result = "Not found"
                except Exception as e:
                    result = f"Error: {e}"
                finally:
                    conn.close()
            else:
                result = "Enter ID"
            self._serve_html(METRICS_PAGE.replace("%RESULT%", result))
        elif path == "/logout":
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
            username = data.get('username',[''])[0]
            password = data.get('password',[''])[0]
            if username == 'guest' and password == 'guest':
                payload = {"user":"guest","role":"user","iat":int(time.time())}
                token = jwt_create(payload)
                self.send_response(302)
                self.send_header("Set-Cookie", f"token={token}; Path=/")
                self.send_header("Location", "/dashboard")
                self.end_headers()
            else:
                self.send_error(403, "Bad credentials")
        else:
            self.send_error(404)

    def _get_token(self):
        cookie = self.headers.get('Cookie','')
        if 'token=' in cookie:
            return cookie.split('token=')[1].split(';')[0]
        return None

    def _clear_auth(self):
        self.send_header("Set-Cookie", "token=; expires=Thu, 01 Jan 1970 00:00:00 GMT")

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

    def _serve_json(self, data):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def log_message(self, format, *args):
        pass

if __name__ == "__main__":
    server = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), PivotHandler)
    print("Web+JWT+SQLi on", PORT, flush=True)
    server.serve_forever()
