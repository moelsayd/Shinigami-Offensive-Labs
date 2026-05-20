#!/usr/bin/env python3
import http.server, sys, json, base64, hmac, hashlib, os, urllib.parse, time, uuid, sqlite3, threading

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 9201
ROOM_DIR = os.path.dirname(os.path.abspath(__file__))
SECRET = b"weak_auth_secret"  # مسرب في backup
DB_PATH = os.path.join(ROOM_DIR, "drift.db")
FLAG_FAKE = "THM{fake_oauth_portal}"

conn = sqlite3.connect(DB_PATH)
conn.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, role TEXT)")
conn.execute("INSERT OR IGNORE INTO users VALUES (1, 'admin', 'admin')")
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
<html><head><title>AuthDrift Portal</title>
<style>body{background:#0a0c10;color:#c9d1d9;font-family:'Segoe UI',sans-serif;display:flex;justify-content:center;align-items:center;height:100vh;margin:0;}
.box{background:#1a1c2b;padding:2rem;border-radius:12px;} h2{color:#e53170;}
input{width:100%;padding:10px;margin:8px 0;background:#0d0f1a;border:1px solid #333;color:white;border-radius:5px;}
input[type=submit]{background:#e53170;border:none;cursor:pointer;font-weight:bold;}
a{color:#58a6ff;}</style></head><body><div class="box"><h2>Login</h2>
<form method="GET" action="/oauth/authorize"><input type="hidden" name="client_id" value="webapp">
<input type="hidden" name="redirect_uri" value="http://localhost:9201/oauth/callback">
<button type="submit">Login via OAuth</button></form>
<!-- Backup config at /backup/config.bak -->
</div></body></html>"""

ROBOTS_TXT = """User-agent: *
Disallow: /backup/
Disallow: /debug
"""

CONFIG = """# Backup Config
JWT_SECRET=weak_auth_secret
OAUTH_SERVER=http://localhost:9202
WEBSOCKET_SERVICE=ws://localhost:9203/ws
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
        elif path == "/backup/config.bak": self._serve_text(CONFIG)
        elif path == "/debug": self._serve_json(DEBUG_PAGE)
        elif path == "/oauth/callback":
            code = qs.get('code', [None])[0]
            if not code:
                self.send_error(400, "Missing code"); return
            # Exchange code for token (محاكاة)
            if code.startswith("oauth_code_"):
                user = code.split("_")[-1]
                token = jwt_create({"user":user, "role":"user", "iat":int(time.time())})
                self.send_response(302)
                self.send_header("Set-Cookie", f"token={token}; Path=/")
                self.send_header("Location", "/dashboard")
                self.end_headers()
            else:
                self.send_error(403, "Invalid code")
        elif path == "/dashboard":
            payload = jwt_verify(token) if token else None
            if not payload: self.send_error(403); return
            role = payload.get("role","user")
            html = f"<h2>Dashboard</h2><p>Welcome {payload['user']}, your role is {role}</p>"
            if role == "admin":
                html += "<p>Access WebSocket service at ws://localhost:9203/ws with token={token}</p>"
            html += '<a href="/logout">Logout</a>'
            self._serve_html(html)
        elif path == "/logout":
            self.send_response(302)
            self.send_header("Set-Cookie","token=; expires=Thu, 01 Jan 1970 00:00:00 GMT")
            self.send_header("Location","/")
            self.end_headers()
        else: self.send_error(404)

    def do_POST(self):
        if self.path == "/oauth/token":
            content_length = int(self.headers.get('Content-Length',0))
            body = self.rfile.read(content_length).decode()
            data = urllib.parse.parse_qs(body)
            # محاكاة صرف رمز
            client_id = data.get('client_id',[''])[0]
            client_secret = data.get('client_secret',[''])[0]
            code = data.get('code',[''])[0]
            if client_id == "webapp" and client_secret == "secret123":
                user = code.split("_")[-1]
                token = jwt_create({"user":user, "role":"user", "iat":int(time.time())})
                self._serve_json({"access_token": token, "token_type": "Bearer"})
            else:
                self.send_error(403)
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
