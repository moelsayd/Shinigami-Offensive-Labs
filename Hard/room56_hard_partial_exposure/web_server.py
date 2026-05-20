#!/usr/bin/env python3
import http.server, sys, json, base64, hmac, hashlib, os, urllib.parse, time, uuid, sqlite3

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 9101
ROOM_DIR = os.path.dirname(os.path.abspath(__file__))
SECRET = b"s3cr3t_k3y!"  # تم تسريبه في config
DB_PATH = os.path.join(ROOM_DIR, "hard.db")
FLAG_FAKE = "THM{fake_web_debug}"

conn = sqlite3.connect(DB_PATH)
conn.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT, ssh_creds TEXT)")
conn.execute("INSERT OR IGNORE INTO users VALUES (1, 'admin', 'admin', 'user', '')")
conn.execute("INSERT OR IGNORE INTO users VALUES (2, 'dev', 'dev123', 'user', '')")
conn.execute("INSERT OR IGNORE INTO users VALUES (3, 'operator', 'hash_only', 'user', 'operator:0p3r4t0rP@ss')")
conn.commit()
conn.close()

def b64e(d): return base64.urlsafe_b64encode(d).rstrip(b'=').decode()
def b64d(d):
    d += '=' * (4 - len(d) % 4)
    return base64.urlsafe_b64decode(d)
def jwt_create(payload, secret=SECRET, alg="HS256"):
    h = b64e(json.dumps({"alg":alg,"typ":"JWT"}).encode())
    p = b64e(json.dumps(payload).encode())
    if alg == "none": return f"{h}.{p}."
    sig = b64e(hmac.new(secret, f"{h}.{p}".encode(), hashlib.sha256).digest())
    return f"{h}.{p}.{sig}"
def jwt_verify(token):
    try:
        h, p, sig = token.split(".")
        header = json.loads(b64d(h))
        if header.get("alg") == "none": return json.loads(b64d(p))
        expected = b64e(hmac.new(SECRET, f"{h}.{p}".encode(), hashlib.sha256).digest())
        if sig != expected: return None
        return json.loads(b64d(p))
    except: return None

LOGIN_HTML = """<!DOCTYPE html>
<html><head><title>SecureCorp Portal</title>
<style>body{background:#0a0c10;display:flex;justify-content:center;align-items:center;height:100vh;font-family:'Segoe UI',sans-serif;}
.box{background:#1a1c2b;padding:2rem;border-radius:12px;} h2{color:#e53170;}
input{width:100%;padding:10px;margin:8px 0;background:#0d0f1a;border:1px solid #333;color:white;border-radius:5px;}
input[type=submit]{background:#e53170;border:none;cursor:pointer;font-weight:bold;}
</style></head><body><div class="box"><h2>Employee Login</h2>
<form method="POST" action="/api/v2/login"><input name="username" placeholder="Username"><br>
<input type="password" name="password" placeholder="Password"><br>
<input type="submit" value="Log In"></form>
</div></body></html>"""

ROBOTS_TXT = """User-agent: *
Disallow: /config/
Disallow: /debug
Disallow: /admin
"""

CONFIG = """# Application Configuration
JWT_SECRET=s3cr3t_k3y!
API_USER=admin
API_PASSWORD_HINT=Check /api/v2/internal/users (admin role required)
INTERNAL_SERVICE=http://localhost:9102/process
"""

DEBUG_PAGE = json.dumps({"status":"ok","fake_flag":FLAG_FAKE})

sessions = {}

class WebHandler(http.server.BaseHTTPRequestHandler):
    def handle_one_request(self):
        try: super().handle_one_request()
        except (ConnectionResetError, BrokenPipeError): pass

    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path
        qs = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        token = self._get_token()

        if path == "/": self._serve_html(LOGIN_HTML)
        elif path == "/robots.txt": self._serve_text(ROBOTS_TXT)
        elif path == "/debug": self._serve_json(DEBUG_PAGE)
        elif path == "/config/app.conf": self._serve_text(CONFIG)
        elif path == "/internal/service-key.txt":
            if not token: self.send_error(403); return
            payload = jwt_verify(token)
            if not payload or payload.get("role")!="admin": self.send_error(403); return
            self._serve_text("X-Service-Token: deser123\n")
        elif path == "/api/v2/user":
            if not token: self.send_error(403); return
            payload = jwt_verify(token)
            if not payload: self.send_error(403); return
            uid = qs.get('id', [str(payload.get("id",0))])[0]
            conn = sqlite3.connect(DB_PATH)
            row = conn.execute("SELECT id, username, role, ssh_creds FROM users WHERE id=?", (uid,)).fetchone()
            conn.close()
            if row:
                data = {"id":row[0],"username":row[1],"role":row[2]}
                if payload.get("role")=="admin" and row[3]: data["ssh_creds"] = row[3]
                self._serve_json(data)
            else: self.send_error(404)
        elif path == "/api/v2/internal/users":
            if not token: self.send_error(403); return
            payload = jwt_verify(token)
            if not payload or payload.get("role")!="admin": self.send_error(403); return
            # يتطلب أيضاً ترويسة داخلية
            if self.headers.get("X-Internal-Role") != "admin":
                self.send_error(403, "Missing X-Internal-Role header"); return
            conn = sqlite3.connect(DB_PATH)
            users = conn.execute("SELECT id, username, role, ssh_creds FROM users").fetchall()
            conn.close()
            result = []
            for u in users:
                entry = {"id":u[0],"username":u[1],"role":u[2]}
                if u[3]: entry["ssh_creds"] = u[3]
                result.append(entry)
            self._serve_json(result)
        elif path == "/logout":
            self.send_response(302)
            self.send_header("Set-Cookie","token=; expires=Thu, 01 Jan 1970 00:00:00 GMT")
            self.send_header("Location","/")
            self.end_headers()
        else: self.send_error(404)

    def do_POST(self):
        if self.path == "/api/v2/login":
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
            else: self.send_error(403, "Invalid credentials")
        else: self.send_error(404)

    def _get_token(self):
        if 'token=' in self.headers.get('Cookie',''):
            return self.headers.get('Cookie','').split('token=')[1].split(';')[0]
        return None

    def _serve_html(self, html):
        self.send_response(200); self.send_header("Content-type","text/html"); self.end_headers(); self.wfile.write(html.encode())
    def _serve_text(self, text):
        self.send_response(200); self.send_header("Content-type","text/plain"); self.end_headers(); self.wfile.write(text.encode())
    def _serve_json(self, data):
        self.send_response(200); self.send_header("Content-type","application/json"); self.end_headers(); self.wfile.write(json.dumps(data).encode())
    def log_message(self, format, *args): pass

if __name__ == "__main__":
    server = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), WebHandler)
    print(f"Web on {PORT}", flush=True)
    server.serve_forever()
