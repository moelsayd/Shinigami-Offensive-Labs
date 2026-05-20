#!/usr/bin/env python3
import http.server, sys, json, os, urllib.parse, uuid, sqlite3, threading

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 9801
ROOM_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(ROOM_DIR, "context.db")
FLAG_FAKE = "THM{fake_context_web}"
YAML_API_KEY = "yaml_api_key_789"

# قاعدة بيانات
conn = sqlite3.connect(DB_PATH)
conn.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, role TEXT, secret TEXT)")
conn.execute("INSERT OR IGNORE INTO users VALUES (1, 'guest', 'user', 'no secret')")
conn.execute("INSERT OR IGNORE INTO users VALUES (2, 'admin', 'admin', 'hidden_admin_secret')")
conn.commit()
conn.close()

LOGIN_HTML = """<!DOCTYPE html>
<html><head><title>ContextCorp</title>
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
</style></head><body>
<h2>Dashboard</h2>
<div class="card"><h3>User Lookup</h3>
<form method="GET" action="/user"><input name="id" placeholder="User ID"><button>Search</button></form>
<div>%RESULT%</div>
</div>
<a href="/logout">Logout</a></body></html>"""

ROBOTS_TXT = """User-agent: *
Disallow: /config/
Disallow: /debug
Disallow: /admin
"""

CONFIG = json.dumps({
    "yaml_service": "http://localhost:9802/process",
    "yaml_api_key": YAML_API_KEY,
    "internal_bot_useragent": "InternalBot/1.0"
})

DEBUG_PAGE = json.dumps({"status":"ok","fake_flag":FLAG_FAKE})

sessions = {}

class ContextHandler(http.server.BaseHTTPRequestHandler):
    def handle_one_request(self):
        try: super().handle_one_request()
        except (ConnectionResetError, BrokenPipeError): pass

    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path
        qs = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        sid = self._get_cookie('session')
        user = sessions.get(sid)
        ua = self.headers.get('User-Agent','')

        if path == "/": self._serve_html(LOGIN_HTML)
        elif path == "/robots.txt": self._serve_text(ROBOTS_TXT)
        elif path == "/config": self._serve_json(CONFIG)
        elif path == "/debug":
            # يعرض معلومات إضافية إذا كان User-Agent هو InternalBot
            if ua == "InternalBot/1.0":
                self._serve_json({"secret": YAML_API_KEY, "flag": FLAG_FAKE})
            else:
                self._serve_json(DEBUG_PAGE)
        elif path == "/user":
            if not user: self.send_error(403); return
            user_id = qs.get('id', [None])[0]
            if not user_id: self.send_error(400); return
            # ثغرة Parameter Pollution: إذا أُرسل id مرتين، تؤخذ القيمة الأخيرة
            if isinstance(user_id, list): user_id = user_id[-1]
            # منع الوصول إلى admin مباشرة
            if user_id == 'admin':
                self._serve_html(DASHBOARD.replace("%RESULT%", "Access denied to admin"))
                return
            conn = sqlite3.connect(DB_PATH)
            row = conn.execute("SELECT username, role, secret FROM users WHERE username=?", (user_id,)).fetchone()
            conn.close()
            if row:
                result = f"User: {row[0]}, Role: {row[1]}"
                if row[2]: result += f", Secret: {row[2]}"
                self._serve_html(DASHBOARD.replace("%RESULT%", result))
            else:
                self._serve_html(DASHBOARD.replace("%RESULT%", "Not found"))
        elif path == "/logout":
            self.send_response(302)
            self.send_header("Set-Cookie","session=; expires=Thu, 01 Jan 1970 00:00:00 GMT")
            self.send_header("Location","/"); self.end_headers()
        else: self.send_error(404)

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length',0))
        body = self.rfile.read(content_length).decode()
        data = urllib.parse.parse_qs(body)
        path = urllib.parse.urlparse(self.path).path

        if path == "/login":
            user = data.get('username',[''])[0]; pwd = data.get('password',[''])[0]
            conn = sqlite3.connect(DB_PATH)
            row = conn.execute("SELECT id, username FROM users WHERE username=? AND password=?", (user,pwd)).fetchone()
            conn.close()
            if row:
                sid = uuid.uuid4().hex; sessions[sid] = {"username":row[1]}
                self.send_response(302)
                self.send_header("Set-Cookie", f"session={sid}; Path=/")
                self.send_header("Location", "/user"); self.end_headers()
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
    server = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), ContextHandler)
    print(f"Web on {PORT}", flush=True)
    server.serve_forever()
