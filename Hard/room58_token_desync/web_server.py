#!/usr/bin/env python3
import http.server, sys, json, base64, hmac, hashlib, os, urllib.parse, time, uuid, sqlite3

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 9301
ROOM_DIR = os.path.dirname(os.path.abspath(__file__))
SECRET = b"graphql_secret_key"  # مسرب في settings
DB_PATH = os.path.join(ROOM_DIR, "main.db")
FLAG_FAKE = "THM{fake_web_admin}"

conn = sqlite3.connect(DB_PATH)
conn.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT)")
conn.execute("INSERT OR IGNORE INTO users VALUES (1, 'admin', 'admin123', 'admin')")
conn.execute("INSERT OR IGNORE INTO users VALUES (2, 'guest', 'guest', 'user')")
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
    except: return None

LOGIN_HTML = """<!DOCTYPE html>
<html><head><title>Desync Corp</title>
<style>body{background:#0a0c10;color:#c9d1d9;font-family:'Segoe UI',sans-serif;display:flex;justify-content:center;align-items:center;height:100vh;margin:0;}
.box{background:#1a1c2b;padding:2rem;border-radius:12px;} h2{color:#e53170;}
input{width:100%;padding:10px;margin:8px 0;background:#0d0f1a;border:1px solid #333;color:white;border-radius:5px;}
input[type=submit]{background:#e53170;border:none;cursor:pointer;font-weight:bold;}
</style></head><body><div class="box"><h2>Employee Login</h2>
<form method="POST" action="/login"><input name="username" placeholder="Username"><br>
<input type="password" name="password" placeholder="Password"><br>
<input type="submit" value="Log In"></form>
</div></body></html>"""

ROBOTS_TXT = """User-agent: *
Disallow: /config/
Disallow: /admin
Disallow: /debug
"""

SETTINGS = json.dumps({
    "jwt_secret": "graphql_secret_key",
    "graphql_service": "http://localhost:9302/graphql",
    "note": "GraphQL introspection enabled for development"
})

DEBUG_PAGE = json.dumps({"status":"ok","fake_flag":FLAG_FAKE})

class WebHandler(http.server.BaseHTTPRequestHandler):
    def handle_one_request(self):
        try: super().handle_one_request()
        except (ConnectionResetError, BrokenPipeError): pass

    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path
        token = self._get_token()

        if path == "/": self._serve_html(LOGIN_HTML)
        elif path == "/robots.txt": self._serve_text(ROBOTS_TXT)
        elif path == "/config/settings.json": self._serve_json(SETTINGS)
        elif path == "/debug": self._serve_json(DEBUG_PAGE)
        elif path == "/admin":
            payload = jwt_verify(token) if token else None
            if not payload or payload.get("role") != "admin":
                self.send_error(403, "Admin role required"); return
            self._serve_html(f"<h2>Admin Panel</h2><p>Flag: {FLAG_FAKE}</p>")
        elif path == "/dashboard":
            payload = jwt_verify(token) if token else None
            if not payload: self.send_error(403); return
            user = payload.get("user","?"); role = payload.get("role","user")
            self._serve_html(f"<h2>Dashboard</h2><p>Welcome {user}, role: {role}</p>")
        elif path == "/logout":
            self.send_response(302)
            self.send_header("Set-Cookie","token=; expires=Thu, 01 Jan 1970 00:00:00 GMT")
            self.send_header("Location","/"); self.end_headers()
        else: self.send_error(404)

    def do_POST(self):
        if self.path == "/login":
            content_length = int(self.headers.get('Content-Length',0))
            body = self.rfile.read(content_length).decode()
            data = urllib.parse.parse_qs(body)
            user = data.get('username',[''])[0]
            pwd = data.get('password',[''])[0]
            conn = sqlite3.connect(DB_PATH)
            row = conn.execute("SELECT id, role FROM users WHERE username=? AND password=?", (user,pwd)).fetchone()
            conn.close()
            if row:
                token = jwt_create({"user":user, "role":row[1], "id":row[0], "iat":int(time.time())})
                self.send_response(302)
                self.send_header("Set-Cookie", f"token={token}; Path=/")
                self.send_header("Location", "/dashboard")
                self.end_headers()
            else: self.send_error(403, "Invalid credentials")
        else: self.send_error(404)

    def _get_token(self):
        cookie = self.headers.get('Cookie','')
        if 'token=' in cookie:
            return cookie.split('token=')[1].split(';')[0]
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
