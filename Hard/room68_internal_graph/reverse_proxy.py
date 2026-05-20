#!/usr/bin/env python3
import http.server, sys, json, os, urllib.parse, uuid, time, sqlite3, socket, re

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 10801
ROOM_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(ROOM_DIR, "proxy.db")
FLAG_FAKE = "THM{fake_web_flag}"

# قاعدة بيانات مستخدمين
conn = sqlite3.connect(DB_PATH)
conn.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT)")
conn.execute("INSERT OR IGNORE INTO users VALUES (1, 'admin', 'admin123', 'user')")
conn.execute("INSERT OR IGNORE INTO users VALUES (2, 'guest', 'guest', 'user')")
conn.commit()
conn.close()

LOGIN_HTML = """<!DOCTYPE html>
<html><head><title>CorpNet Portal</title>
<style>body{background:#0a0c10;color:#c9d1d9;font-family:'Segoe UI',sans-serif;display:flex;justify-content:center;align-items:center;height:100vh;margin:0;}
.box{background:#1a1c2b;padding:2rem;border-radius:12px;} h2{color:#e53170;}
input{width:100%;padding:10px;margin:8px 0;background:#0d0f1a;border:1px solid #333;color:white;border-radius:5px;}
input[type=submit]{background:#e53170;border:none;cursor:pointer;font-weight:bold;}
</style></head><body><div class="box"><h2>Login</h2>
<form method="POST" action="/login"><input name="username" placeholder="Username"><br>
<input type="password" name="password" placeholder="Password"><br>
<input type="submit" value="Log In"></form>
</div></body></html>"""

DASHBOARD = """<html><head><title>Dashboard</title>
<style>body{background:#0a0c10;color:#c9d1d9;font-family:'Segoe UI',sans-serif;padding:2rem;}
h2{color:#00ff00;} .card{background:#1a1c2b;padding:1rem;border-radius:8px;margin:1rem 0;}
input,button{padding:8px;margin:5px;border-radius:5px;} input{background:#0d0f1a;border:1px solid #333;color:white;}
button{background:#e53170;border:none;color:white;font-weight:bold;cursor:pointer;}
.result{background:#0d0f1a;padding:1rem;margin-top:1rem;border-radius:5px;white-space:pre-wrap;}
</style></head><body>
<h2>Dashboard</h2>
<div class="card"><h3>URL Fetcher</h3>
<form method="GET" action="/fetch"><input name="url" placeholder="http://external-site.com"><button>Fetch</button></form>
<div class="result">%RESULT%</div>
</div>
<a href="/logout?next=/">Logout</a></body></html>"""

ROBOTS_TXT = """User-agent: *
Disallow: /admin
Disallow: /debug
"""

DEBUG_PAGE = json.dumps({"status":"ok","fake_flag":FLAG_FAKE})

sessions = {}
rate_limit = {}  # لتقييد معدل الطلبات

class ProxyHandler(http.server.BaseHTTPRequestHandler):
    def handle_one_request(self):
        try: super().handle_one_request()
        except (ConnectionResetError, BrokenPipeError): pass

    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path
        qs = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        client_ip = self.client_address[0]

        # Rate limiting
        now = time.time()
        rate_limit.setdefault(client_ip, []).append(now)
        rate_limit[client_ip] = [t for t in rate_limit[client_ip] if now - t < 10]
        if len(rate_limit[client_ip]) > 20:
            self.send_error(429, "Rate limit exceeded")
            return

        if path == "/": self._serve_html(LOGIN_HTML)
        elif path == "/robots.txt": self._serve_text(ROBOTS_TXT)
        elif path == "/debug": self._serve_json(DEBUG_PAGE)
        elif path == "/redirect":
            # Open Redirect (يُستخدم لتجاوز فلتر SSRF)
            url = qs.get('url', [None])[0]
            if url:
                self.send_response(302)
                self.send_header("Location", url)
                self.end_headers()
            else:
                self.send_error(400)
        elif path == "/fetch":
            url = qs.get('url', [None])[0]
            if not url:
                self.send_error(400, "Missing url"); return
            # فلتر SSRF
            parsed = urllib.parse.urlparse(url)
            host = parsed.hostname
            if host in ['127.0.0.1', 'localhost', '0.0.0.0']:
                self._serve_html(DASHBOARD.replace("%RESULT%", "Blocked: internal host"))
                return
            try:
                import urllib.request
                req = urllib.request.Request(url)
                with urllib.request.urlopen(req, timeout=3) as resp:
                    data = resp.read().decode()
                self._serve_html(DASHBOARD.replace("%RESULT%", data))
            except Exception as e:
                self._serve_html(DASHBOARD.replace("%RESULT%", f"Error: {e}"))
        elif path == "/dashboard":
            token = self._get_cookie('token')
            if not token or token not in sessions:
                self.send_error(403); return
            self._serve_html(DASHBOARD.replace("%RESULT%", ""))
        elif path == "/logout":
            self.send_response(302)
            self.send_header("Set-Cookie","token=; expires=Thu, 01 Jan 1970 00:00:00 GMT")
            next_url = qs.get('next', ['/'])[0]
            self.send_header("Location", next_url)
            self.end_headers()
        else: self.send_error(404)

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length',0))
        body = self.rfile.read(content_length).decode()
        path = urllib.parse.urlparse(self.path).path
        if path == "/login":
            data = urllib.parse.parse_qs(body)
            user = data.get('username',[''])[0]; pwd = data.get('password',[''])[0]
            conn = sqlite3.connect(DB_PATH)
            row = conn.execute("SELECT id, username FROM users WHERE username=? AND password=?", (user,pwd)).fetchone()
            conn.close()
            if row:
                sid = uuid.uuid4().hex; sessions[sid] = {"username":row[1]}
                self.send_response(302)
                self.send_header("Set-Cookie", f"token={sid}; Path=/")
                self.send_header("Location", "/dashboard"); self.end_headers()
            else: self.send_error(403, "Invalid credentials")
        else: self.send_error(404)

    def _get_cookie(self, key):
        cookie = self.headers.get('Cookie','')
        if f'{key}=' in cookie:
            return cookie.split(f'{key}=')[1].split(';')[0]
        return None

    def _serve_html(self, html):
        self.send_response(200); self.send_header("Content-type","text/html"); self.end_headers(); self.wfile.write(html.encode())
    def _serve_text(self, text):
        self.send_response(200); self.send_header("Content-type","text/plain"); self.end_headers(); self.wfile.write(text.encode())
    def _serve_json(self, data):
        self.send_response(200); self.send_header("Content-type","application/json"); self.end_headers(); self.wfile.write(json.dumps(data).encode())
    def log_message(self, format, *args): pass

if __name__ == "__main__":
    server = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), ProxyHandler)
    print(f"Proxy on {PORT}", flush=True)
    server.serve_forever()
