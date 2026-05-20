#!/usr/bin/env python3
import http.server, sys, json, os, urllib.parse, uuid, time, sqlite3, base64, hmac, hashlib, socket

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 10201
ROOM_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(ROOM_DIR, "micro.db")
SECRET_MAIN = b"main_secret_123"
INTERNAL_HOST = "127.0.0.1"
INTERNAL_PORT = 10202
FLAG_FAKE = "THM{fake_main_portal}"

# قاعدة بيانات
conn = sqlite3.connect(DB_PATH)
conn.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT)")
conn.execute("INSERT OR IGNORE INTO users VALUES (1, 'admin', 'admin123', 'user')")
conn.execute("INSERT OR IGNORE INTO users VALUES (2, 'guest', 'guest', 'user')")
conn.commit()
conn.close()

def b64e(d): return base64.urlsafe_b64encode(d).rstrip(b'=').decode()
def b64d(d):
    d += '=' * (4 - len(d) % 4)
    return base64.urlsafe_b64decode(d)
def jwt_create(payload, secret=SECRET_MAIN, kid="main_key", alg="HS256"):
    header = {"alg":alg,"typ":"JWT","kid":kid}
    h = b64e(json.dumps(header).encode())
    p = b64e(json.dumps(payload).encode())
    if alg == "none": return f"{h}.{p}."
    sig = b64e(hmac.new(secret, f"{h}.{p}".encode(), hashlib.sha256).digest())
    return f"{h}.{p}.{sig}"
def jwt_verify(token, secret=SECRET_MAIN):
    try:
        h, p, sig = token.split(".")
        header = json.loads(b64d(h))
        if header.get("alg") == "none":
            return json.loads(b64d(p))
        expected = b64e(hmac.new(secret, f"{h}.{p}".encode(), hashlib.sha256).digest())
        if sig != expected: return None
        return json.loads(b64d(p))
    except: return None

LOGIN_HTML = """<!DOCTYPE html>
<html><head><title>MicroCorp</title>
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
input,textarea,button{padding:8px;margin:5px;border-radius:5px;} input,textarea{background:#0d0f1a;border:1px solid #333;color:white;width:100%;}
button{background:#e53170;border:none;color:white;font-weight:bold;cursor:pointer;}
</style></head><body>
<h2>Dashboard</h2>
<div class="card"><h3>Internal Proxy</h3>
<p>Send raw HTTP request to internal service (simulated smuggling):</p>
<form method="POST" action="/proxy"><textarea name="raw_request" placeholder="GET /internal/admin HTTP/1.1\r\nHost: localhost\r\n..."></textarea><br>
<button>Forward</button></form>
<div>%RESULT%</div>
</div>
<a href="/logout">Logout</a></body></html>"""

ROBOTS_TXT = """User-agent: *
Disallow: /debug
Disallow: /config
"""

CONFIG = json.dumps({
    "internal_service": f"http://{INTERNAL_HOST}:{INTERNAL_PORT}",
    "jwt_kid_hint": "Internal service trusts kid parameter from token header"
})

DEBUG_PAGE = json.dumps({"status":"ok","fake_flag":FLAG_FAKE})

sessions = {}

class WebHandler(http.server.BaseHTTPRequestHandler):
    def handle_one_request(self):
        try: super().handle_one_request()
        except (ConnectionResetError, BrokenPipeError): pass

    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path
        if path == "/": self._serve_html(LOGIN_HTML)
        elif path == "/robots.txt": self._serve_text(ROBOTS_TXT)
        elif path == "/config": self._serve_json(CONFIG)
        elif path == "/debug": self._serve_json(DEBUG_PAGE)
        elif path == "/dashboard":
            token = self._get_cookie('token')
            if not token or token not in sessions:
                self.send_error(403); return
            user = sessions[token]
            self._serve_html(DASHBOARD.replace("%RESULT%", ""))
        elif path == "/logout":
            self.send_response(302)
            self.send_header("Set-Cookie","token=; expires=Thu, 01 Jan 1970 00:00:00 GMT")
            self.send_header("Location","/"); self.end_headers()
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
                sid = uuid.uuid4().hex
                sessions[sid] = {"username":row[1],"role":"user"}
                token = jwt_create({"user":row[1],"role":"user","id":row[0],"iat":int(time.time())})
                self.send_response(302)
                self.send_header("Set-Cookie", f"token={token}; Path=/")
                self.send_header("Location", "/dashboard"); self.end_headers()
            else: self.send_error(403, "Invalid credentials")
        elif path == "/proxy":
            data = urllib.parse.parse_qs(body)
            raw_request = data.get('raw_request',[''])[0]
            if not raw_request:
                self.send_error(400, "Missing raw_request"); return
            # إرسال الطلب الخام إلى الخدمة الداخلية
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(5)
                s.connect((INTERNAL_HOST, INTERNAL_PORT))
                s.sendall(raw_request.encode() + b"\r\n")
                response = b""
                while True:
                    chunk = s.recv(4096)
                    if not chunk: break
                    response += chunk
                s.close()
                result = response.decode(errors='ignore')
            except Exception as e:
                result = f"Proxy error: {e}"
            self._serve_html(DASHBOARD.replace("%RESULT%", f"<pre>{result}</pre>"))
        else:
            self.send_error(404)

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
    server = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), WebHandler)
    print(f"Web on {PORT}", flush=True)
    server.serve_forever()
