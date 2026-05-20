#!/usr/bin/env python3
import http.server, sys, json, base64, hmac, hashlib, os, urllib.parse, time, uuid, sqlite3

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8801
ROOM_DIR = os.path.dirname(os.path.abspath(__file__))
SECRET = b"dev_secret_key"  # مسرب في backup
FLAG_FAKE = "THM{fake_main_portal}"
DB_PATH = os.path.join(ROOM_DIR, "main.db")

# قاعدة بيانات
conn = sqlite3.connect(DB_PATH)
conn.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT)")
conn.execute("INSERT OR IGNORE INTO users VALUES (1, 'admin', 'admin123', 'admin')")
conn.execute("INSERT OR IGNORE INTO users VALUES (2, 'dev', 'dev123', 'user')")
conn.commit()
conn.close()

def b64e(d): return base64.urlsafe_b64encode(d).rstrip(b'=').decode()
def b64d(d):
    d += '=' * (4 - len(d) % 4)
    return base64.urlsafe_b64decode(d)
def jwt_create(payload, secret=SECRET, alg="HS256"):
    header = {"alg":alg,"typ":"JWT"}
    h = b64e(json.dumps(header).encode())
    p = b64e(json.dumps(payload).encode())
    if alg == "none": return f"{h}.{p}."
    sig = b64e(hmac.new(secret, f"{h}.{p}".encode(), hashlib.sha256).digest())
    return f"{h}.{p}.{sig}"
def jwt_verify(token):
    try:
        h, p, sig = token.split(".")
        header = json.loads(b64d(h))
        if header.get("alg") == "none":
            return json.loads(b64d(p))
        expected = b64e(hmac.new(SECRET, f"{h}.{p}".encode(), hashlib.sha256).digest())
        if sig != expected: return None
        return json.loads(b64d(p))
    except:
        return None

MAIN_SITE = """<!DOCTYPE html>
<html><head><title>NeoCorp Main</title>
<style>body{background:#0a0c10;color:#c9d1d9;font-family:'Segoe UI',sans-serif;padding:2rem;}
h1{color:#f0883e;}</style></head><body><h1>NeoCorp Public Site</h1>
<!-- Dev: staging.neocorp.local -->
</body></html>"""

STAGING_LOGIN = """<!DOCTYPE html>
<html><head><title>Staging Portal</title>
<style>body{background:#0a0c10;display:flex;justify-content:center;align-items:center;height:100vh;font-family:'Segoe UI',sans-serif;}
.box{background:#1a1c2b;padding:2rem;border-radius:12px;} h2{color:#00ff00;}
input{width:100%;padding:10px;margin:8px 0;background:#0d0f1a;border:1px solid #333;color:white;border-radius:5px;}
input[type=submit]{background:#00aa00;border:none;cursor:pointer;font-weight:bold;}
</style></head><body><div class="box"><h2>Staging Portal</h2>
<form method="POST" action="/login"><input name="username" placeholder="Username"><br>
<input type="password" name="password" placeholder="Password"><br>
<input type="submit" value="Log In"></form>
</div></body></html>"""

ROBOTS_TXT = """User-agent: *
Disallow: /backup/
Disallow: /debug
"""

BACKUP_CONFIG = f"""JWT_SECRET=dev_secret_key
API_URL=http://localhost:8802
API_USER=admin
API_PASS=NoSQL_P@ss
"""

DEBUG_PAGE = json.dumps({"status":"debug","fake_flag":FLAG_FAKE})

sessions = {}

class WebHandler(http.server.BaseHTTPRequestHandler):
    def handle_one_request(self):
        try: super().handle_one_request()
        except: pass

    def do_GET(self):
        host = self.headers.get('Host','').split(':')[0]
        path = urllib.parse.urlparse(self.path).path
        if host == 'localhost' or host == '127.0.0.1':
            if path == '/': self._serve_html(MAIN_SITE)
            elif path == '/robots.txt': self._serve_text(ROBOTS_TXT)
            elif path == '/debug': self._serve_json(DEBUG_PAGE)
            else: self.send_error(404)
        elif host == 'staging.neocorp.local':
            if path == '/': self._serve_html(STAGING_LOGIN)
            elif path == '/robots.txt': self._serve_text(ROBOTS_TXT)
            elif path == '/backup/config.bak': self._serve_text(BACKUP_CONFIG)
            elif path == '/debug': self._serve_json(DEBUG_PAGE)
            else: self.send_error(404)
        else:
            self.send_error(404)

    def do_POST(self):
        if urllib.parse.urlparse(self.path).path == '/login':
            content_length = int(self.headers.get('Content-Length',0))
            body = self.rfile.read(content_length).decode()
            data = urllib.parse.parse_qs(body)
            user = data.get('username',[''])[0]
            pwd = data.get('password',[''])[0]
            conn = sqlite3.connect(DB_PATH)
            row = conn.execute("SELECT id, role FROM users WHERE username=? AND password=?", (user,pwd)).fetchone()
            conn.close()
            if row:
                token = jwt_create({"user":user,"role":row[1],"id":row[0],"iat":int(time.time())})
                self.send_response(302)
                self.send_header("Set-Cookie", f"token={token}; Path=/")
                self.send_header("Location", "/")
                self.end_headers()
            else:
                self.send_error(403, "Invalid credentials")
        else:
            self.send_error(404)

    def _serve_html(self, html):
        self.send_response(200); self.send_header("Content-type","text/html"); self.end_headers(); self.wfile.write(html.encode())
    def _serve_text(self, text):
        self.send_response(200); self.send_header("Content-type","text/plain"); self.end_headers(); self.wfile.write(text.encode())
    def _serve_json(self, data):
        self.send_response(200); self.send_header("Content-type","application/json"); self.end_headers(); self.wfile.write(json.dumps(data).encode())
    def log_message(self, format, *args): pass

if __name__ == "__main__":
    server = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), WebHandler)
    print(f"Web server on {PORT}", flush=True)
    server.serve_forever()
