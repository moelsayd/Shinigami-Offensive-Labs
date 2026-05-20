#!/usr/bin/env python3
import http.server, sys, json, sqlite3, os, urllib.parse, base64, hmac, hashlib, time

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 7083
ROOM_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(ROOM_DIR, "expansion.db")
FLAG = "THM{api_exp4ns10n_sqli}"
FAKE_FLAG1 = "THM{fake_internal_flag}"
FAKE_FLAG2 = "THM{fake_debug_flag}"
SECRET = b"secret123"   # تم تسريبه في debug

# ======================= JWT Mini-library =======================
def b64url_encode(data):
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode()
def b64url_decode(data):
    padding = 4 - len(data) % 4
    if padding != 4:
        data += '=' * padding
    return base64.urlsafe_b64decode(data)
def jwt_create(payload, secret, alg="HS256"):
    header = {"alg": alg, "typ": "JWT"}
    h = b64url_encode(json.dumps(header, separators=(",", ":")).encode())
    p = b64url_encode(json.dumps(payload, separators=(",", ":")).encode())
    sig = hmac.new(secret, f"{h}.{p}".encode(), hashlib.sha256).digest()
    return f"{h}.{p}.{b64url_encode(sig)}"
def jwt_verify(token, secret):
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        header = json.loads(b64url_decode(parts[0]))
        if header.get("alg") == "none":
            return json.loads(b64url_decode(parts[1]))
        sig_expected = b64url_encode(hmac.new(secret, f"{parts[0]}.{parts[1]}".encode(), hashlib.sha256).digest())
        if parts[2] != sig_expected:
            return None
        return json.loads(b64url_decode(parts[1]))
    except:
        return None

# ======================= HTML Templates =======================
INDEX_HTML = """<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><title>API Portal</title>
<style>body{background:#0a0c10;color:#c9d1d9;font-family:'Segoe UI',sans-serif;padding:2rem;}
h1{color:#f0883e;} a{color:#58a6ff;}</style></head><body>
<h1>API Portal</h1>
<ul><li><a href="/api/v1/user?id=1">/api/v1/user</a></li>
<li><a href="/api/v1/admin">/api/v1/admin</a></li></ul>
<script src="/static/api-map.js"></script></body></html>"""

API_MAP_JS = """// API Map for version 2 (internal test)
// TODO: add /api/v2/internal/flag to production
console.log("API map loaded");"""

ROBOTS_TXT = """User-agent: *
Disallow: /api/
Disallow: /debug/
Disallow: /static/
Disallow: /console
"""

DEBUG_CONFIG = json.dumps({
    "jwt_secret": "secret123",
    "alg": "HS256",
    "debug_endpoints": ["/debug/config", "/debug/flag"]
})

DEBUG_FLAG_HTML = f"""<html><body><h1>Debug Flag</h1><p>{FAKE_FLAG2}</p></body></html>"""

class APIHandler(http.server.BaseHTTPRequestHandler):
    def handle_one_request(self):
        try:
            super().handle_one_request()
        except (ConnectionResetError, BrokenPipeError):
            pass

    # ======================= GET =======================
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        qs = urllib.parse.parse_qs(parsed.query)
        token = self._get_token()

        if path == "/":
            self._serve_html(INDEX_HTML)
        elif path == "/robots.txt":
            self._serve_text(ROBOTS_TXT)
        elif path == "/static/api-map.js":
            self._serve_text(API_MAP_JS, "application/javascript")
        elif path == "/debug/config":
            self._serve_text(DEBUG_CONFIG, "application/json")
        elif path == "/debug/flag":
            self._serve_html(DEBUG_FLAG_HTML)
        elif path == "/api/v1/user":
            uid = qs.get('id', [''])[0]
            if uid == '1':
                self._serve_json({"id":1, "name":"John", "role":"user"})
            else:
                self._serve_json({"error":"User not found"}, 404)
        elif path == "/api/v1/admin":
            payload = jwt_verify(token, SECRET) if token else None
            if not payload or payload.get("role") != "admin":
                self._serve_json({"error":"Admin access required"}, 403)
                return
            # Admin dashboard with link to internal flag
            admin_html = f"""<html><head><title>Admin Panel</title>
<style>body{{background:#0a0c10;color:#c9d1d9;font-family:'Segoe UI',sans-serif;padding:2rem;}}
h2{{color:#00ff00;}} a{{color:#58a6ff;}}</style></head><body>
<h2>Admin Panel</h2>
<p>Use the internal flag endpoint: <a href="/api/v2/internal/flag?id=1">/api/v2/internal/flag?id=1</a></p>
<a href="/logout">Logout</a></body></html>"""
            self._serve_html(admin_html)
        elif path == "/api/v2/internal/flag":
            payload = jwt_verify(token, SECRET) if token else None
            if not payload or payload.get("role") != "admin":
                self._serve_json({"error":"Admin access required"}, 403)
                return
            uid = qs.get('id', [''])[0]
            if uid:
                conn = sqlite3.connect(DB_PATH)
                try:
                    # SQLi vulnerable
                    row = conn.execute(f"SELECT data FROM flags WHERE id = {uid}").fetchone()
                    result = row[0] if row else "Not found"
                except Exception as e:
                    result = f"Error: {e}"
                finally:
                    conn.close()
                self._serve_text(result)
            else:
                self._serve_text("Please provide id parameter")
        elif path == "/login":
            # صفحة تسجيل الدخول بسيطة
            login_html = """<html><head><title>Login</title>
<style>body{background:#0a0c10;display:flex;justify-content:center;align-items:center;height:100vh;font-family:'Segoe UI',sans-serif;}
.box{background:#1a1c2b;padding:2rem;border-radius:12px;} h2{color:#00ff00;}
input{width:100%;padding:10px;margin:8px 0;background:#0d0f1a;border:1px solid #333;color:white;border-radius:5px;}
input[type=submit]{background:#00aa00;border:none;cursor:pointer;}</style></head><body>
<div class="box"><h2>API Login</h2><form method="POST" action="/login">
<input name="username" placeholder="Username"><br>
<input type="password" name="password" placeholder="Password"><br>
<input type="submit" value="Login"></form></div></body></html>"""
            self._serve_html(login_html)
        elif path == "/logout":
            self.send_response(302)
            self.send_header("Set-Cookie", "token=; expires=Thu, 01 Jan 1970 00:00:00 GMT")
            self.send_header("Location", "/")
            self.end_headers()
        else:
            self.send_error(404)

    # ======================= POST =======================
    def do_POST(self):
        if self.path == "/login":
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode()
            data = urllib.parse.parse_qs(body)
            user = data.get('username', [''])[0]
            pwd = data.get('password', [''])[0]
            if user == 'guest' and pwd == 'guest':
                payload = {"user":"guest", "role":"user", "iat": int(time.time())}
                token = jwt_create(payload, SECRET)
                self.send_response(302)
                self.send_header("Set-Cookie", f"token={token}; Path=/")
                self.send_header("Location", "/api/v1/user?id=1")
                self.end_headers()
            else:
                self.send_error(403, "Bad credentials")
        else:
            self.send_error(404)

    # ======================= Helpers =======================
    def _get_token(self):
        cookie = self.headers.get('Cookie', '')
        if 'token=' in cookie:
            return cookie.split('token=')[1].split(';')[0]
        return None

    def _serve_html(self, html):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode())

    def _serve_text(self, text, ctype="text/plain"):
        self.send_response(200)
        self.send_header("Content-type", ctype)
        self.end_headers()
        self.wfile.write(text.encode())

    def _serve_json(self, data, code=200):
        self.send_response(code)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def log_message(self, format, *args):
        pass

if __name__ == "__main__":
    server = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), APIHandler)
    print("Server active", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
