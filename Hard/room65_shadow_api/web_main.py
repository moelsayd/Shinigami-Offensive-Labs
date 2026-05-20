#!/usr/bin/env python3
import http.server, sys, json, os, urllib.parse, uuid, time, sqlite3, base64, hmac, hashlib

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 10010
ROOM_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(ROOM_DIR, "shadow.db")
SECRET = b"shadow_api_secret"  # مسرب في JS
FLAG_FAKE = "THM{fake_web_portal}"

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
<html><head><title>ShadowApp</title>
<style>body{background:#0a0c10;color:#c9d1d9;font-family:'Segoe UI',sans-serif;display:flex;justify-content:center;align-items:center;height:100vh;margin:0;}
.box{background:#1a1c2b;padding:2rem;border-radius:12px;} h2{color:#e53170;}
input{width:100%;padding:10px;margin:8px 0;background:#0d0f1a;border:1px solid #333;color:white;border-radius:5px;}
input[type=submit]{background:#e53170;border:none;cursor:pointer;font-weight:bold;}
</style></head><body><div class="box"><h2>Login</h2>
<form method="POST" action="/login"><input name="username" placeholder="Username"><br>
<input type="password" name="password" placeholder="Password"><br>
<input type="submit" value="Log In"></form>
</div><script src="/assets/app.js"></script></body></html>"""

APP_JS = """// ShadowApp Mobile API config
window.SHADOW_CONFIG = {
    API_BASE: "/api/v2/",
    ADMIN_PANEL: "/internal/admin",
    WS_SERVICE: "ws://localhost:10040/ws",
    JWT_SECRET: "shadow_api_secret",
    DEBUG: true
};
console.log("App loaded");"""

ROBOTS_TXT = """User-agent: *
Disallow: /api/
Disallow: /internal/
Disallow: /debug
"""

DEBUG_PAGE = json.dumps({"status":"ok","fake_flag":FLAG_FAKE})

sessions = {}

class WebHandler(http.server.BaseHTTPRequestHandler):
    def handle_one_request(self):
        try: super().handle_one_request()
        except (ConnectionResetError, BrokenPipeError): pass

    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path
        if path == "/": self._serve_html(LOGIN_HTML)
        elif path == "/assets/app.js": self._serve_text(APP_JS, "application/javascript")
        elif path == "/robots.txt": self._serve_text(ROBOTS_TXT)
        elif path == "/debug": self._serve_json(DEBUG_PAGE)
        elif path == "/dashboard":
            token = self._get_token()
            payload = jwt_verify(token) if token else None
            if not payload: self.send_error(403); return
            role = payload.get("role","user")
            html = f"<h2>Dashboard</h2><p>Welcome {payload.get('user','?')}, role: {role}</p>"
            if role == "admin":
                html += "<p>Access internal API at <a href='http://localhost:10020/docs'>http://localhost:10020/docs</a></p>"
            self._serve_html(html)
        elif path == "/logout":
            self.send_response(302)
            self.send_header("Set-Cookie","token=; expires=Thu, 01 Jan 1970 00:00:00 GMT")
            self.send_header("Location","/"); self.end_headers()
        else: self.send_error(404)

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length',0))
        body = self.rfile.read(content_length).decode()
        data = urllib.parse.parse_qs(body)
        if self.path == "/login":
            user = data.get('username',[''])[0]; pwd = data.get('password',[''])[0]
            conn = sqlite3.connect(DB_PATH)
            row = conn.execute("SELECT id, role FROM users WHERE username=? AND password=?", (user,pwd)).fetchone()
            conn.close()
            if row:
                token = jwt_create({"user":user, "role":row[1], "id":row[0], "iat":int(time.time())})
                self.send_response(302)
                self.send_header("Set-Cookie", f"token={token}; Path=/")
                self.send_header("Location", "/dashboard"); self.end_headers()
            else: self.send_error(403, "Invalid credentials")
        else: self.send_error(404)

    def _get_token(self):
        cookie = self.headers.get('Cookie','')
        if 'token=' in cookie:
            return cookie.split('token=')[1].split(';')[0]
        return None

    def _serve_html(self, html):
        self.send_response(200); self.send_header("Content-type","text/html"); self.end_headers(); self.wfile.write(html.encode())
    def _serve_text(self, text, ctype="text/plain"):
        self.send_response(200); self.send_header("Content-type",ctype); self.end_headers(); self.wfile.write(text.encode())
    def _serve_json(self, data):
        self.send_response(200); self.send_header("Content-type","application/json"); self.end_headers(); self.wfile.write(json.dumps(data).encode())
    def log_message(self, format, *args): pass

if __name__ == "__main__":
    server = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), WebHandler)
    print(f"Web on {PORT}", flush=True)
    server.serve_forever()
