#!/usr/bin/env python3
import http.server, sys, json, base64, hmac, hashlib, os, urllib.parse, time, uuid, sqlite3, re

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8701
ROOM_DIR = os.path.dirname(os.path.abspath(__file__))
SECRET = b"supersecretkey"  # تم تسريبه في APK
DB_PATH = os.path.join(ROOM_DIR, "api.db")
FLAG_REAL = "THM{adb_burp_jwt_nosql_idor}"
FLAG_FAKE = "THM{fake_api_debug}"

# ---------- قاعدة بيانات ----------
conn = sqlite3.connect(DB_PATH)
conn.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT, secret TEXT)")
conn.execute("INSERT OR IGNORE INTO users VALUES (1, 'admin', 'admin123', 'admin', ?)", (FLAG_FAKE,))
conn.execute("INSERT OR IGNORE INTO users VALUES (2, 'guest', 'guest', 'user', '')")
conn.execute("INSERT OR IGNORE INTO users VALUES (3, 'flagholder', 'nopass', 'user', ?)", (FLAG_REAL,))
conn.commit()
conn.close()

# ---------- JWT ----------
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
        if header.get("alg") == "none":
            return json.loads(b64d(p))
        expected = b64e(hmac.new(SECRET, f"{h}.{p}".encode(), hashlib.sha256).digest())
        if sig != expected:
            return None
        return json.loads(b64d(p))
    except:
        return None

# ---------- HTML ----------
LOGIN_PAGE = """<!DOCTYPE html>
<html><head><title>NeoApp API</title>
<style>body{background:#0a0c10;color:#c9d1d9;font-family:'Segoe UI',sans-serif;display:flex;justify-content:center;align-items:center;height:100vh;margin:0;}
.box{background:#1a1c2b;padding:2rem;border-radius:12px;} h2{color:#e53170;}
input{width:100%;padding:10px;margin:8px 0;background:#0d0f1a;border:1px solid #333;color:white;border-radius:5px;}
input[type=submit]{background:#e53170;border:none;cursor:pointer;font-weight:bold;}
</style></head><body><div class="box"><h2>NeoApp Login</h2>
<form method="POST" action="/api/login"><input name="username" placeholder="Username"><br>
<input type="password" name="password" placeholder="Password"><br>
<input type="submit" value="Log In"></form>
</div></body></html>"""

DASHBOARD = """<html><head><title>Dashboard</title>
<style>body{background:#0a0c10;color:#c9d1d9;font-family:'Segoe UI',sans-serif;padding:2rem;}
h2{color:#00ff00;} .card{background:#1a1c2b;padding:1rem;border-radius:8px;margin:1rem 0;}
a{color:#58a6ff;}</style></head><body>
<h2>Welcome, {user}</h2>
<div class="card"><p>Role: {role}</p></div>
<div class="card"><h3>User Search (admin only)</h3>
<form method="GET" action="/api/admin/users"><input name="query" placeholder='{"username":"admin"}'><button>Search</button></form>
</div><a href="/api/profile?user_id={user_id}">My Profile</a><br><a href="/logout">Logout</a></body></html>"""

PROFILE_PAGE = """<html><head><title>Profile</title>
<style>body{background:#0a0c10;color:#c9d1d9;font-family:'Segoe UI',sans-serif;padding:2rem;}
pre{background:#0d0f1a;padding:1rem;border-radius:5px;}</style></head><body>
<h2>Profile</h2><pre>{data}</pre><a href="/dashboard">Back</a></body></html>"""

ROBOTS_TXT = """User-agent: *
Disallow: /debug
Disallow: /api/admin
"""

DEBUG = json.dumps({"status":"debug","jwt_secret_hint":"supersecretkey","fake_flag":FLAG_FAKE})

sessions = {}

class APIHandler(http.server.BaseHTTPRequestHandler):
    def handle_one_request(self):
        try:
            super().handle_one_request()
        except (ConnectionResetError, BrokenPipeError):
            pass

    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path
        qs = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
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
            user = payload.get("user","unknown")
            role = payload.get("role","user")
            uid = payload.get("id",0)
            self._serve_html(DASHBOARD.replace("{user}",user).replace("{role}",role).replace("{user_id}",str(uid)))
        elif path == "/api/profile":
            payload = jwt_verify(token) if token else None
            if not payload:
                self.send_error(403); return
            target_id = qs.get('user_id', [str(payload.get("id",0))])[0]
            conn = sqlite3.connect(DB_PATH)
            row = conn.execute("SELECT username, role, secret FROM users WHERE id=?", (target_id,)).fetchone()
            conn.close()
            if row:
                text = f"Username: {row[0]}\nRole: {row[1]}"
                if row[2]:
                    text += f"\nSecret: {row[2]}"
                self._serve_html(PROFILE_PAGE.replace("{data}", text))
            else:
                self.send_error(404)
        elif path == "/api/admin/users":
            payload = jwt_verify(token) if token else None
            if not payload or payload.get("role") != "admin":
                self.send_error(403); return
            query = qs.get('query', [None])[0]
            if not query:
                self.send_error(400); return
            try:
                query_obj = json.loads(query)
            except:
                self.send_error(400, "Invalid JSON query")
                return
            conn = sqlite3.connect(DB_PATH)
            # محاكاة NoSQL: نطبق query على قاعدة البيانات
            all_users = conn.execute("SELECT id, username, role, secret FROM users").fetchall()
            results = []
            for u in all_users:
                match = True
                user_dict = {"id":u[0],"username":u[1],"role":u[2],"secret":u[3]}
                for k,v in query_obj.items():
                    if isinstance(v, dict):
                        if "$ne" in v and user_dict.get(k) == v["$ne"]:
                            match = False
                        if "$regex" in v:
                            if not re.search(v["$regex"], str(user_dict.get(k,"")), re.IGNORECASE):
                                match = False
                    else:
                        if user_dict.get(k) != v:
                            match = False
                if match:
                    results.append(user_dict)
            conn.close()
            self._serve_json(results)
        elif path == "/logout":
            self.send_response(302)
            self.send_header("Set-Cookie","token=; expires=Thu, 01 Jan 1970 00:00:00 GMT")
            self.send_header("Location","/")
            self.end_headers()
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path == "/api/login":
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode()
            data = urllib.parse.parse_qs(body)
            user = data.get('username',[''])[0]
            pwd = data.get('password',[''])[0]
            conn = sqlite3.connect(DB_PATH)
            row = conn.execute("SELECT id, username, role FROM users WHERE username=? AND password=?", (user, pwd)).fetchone()
            conn.close()
            if row:
                payload = {"user":row[1],"role":row[2],"id":row[0],"iat":int(time.time())}
                token = jwt_create(payload)
                self.send_response(302)
                self.send_header("Set-Cookie", f"token={token}; Path=/")
                self.send_header("Location", "/dashboard")
                self.end_headers()
            else:
                self.send_error(403, "Invalid credentials")
        else:
            self.send_error(404)

    def _get_token(self):
        cookie = self.headers.get('Cookie','')
        if 'token=' in cookie:
            return cookie.split('token=')[1].split(';')[0]
        return None

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
    server = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), APIHandler)
    print(f"API server on {PORT}", flush=True)
    server.serve_forever()
