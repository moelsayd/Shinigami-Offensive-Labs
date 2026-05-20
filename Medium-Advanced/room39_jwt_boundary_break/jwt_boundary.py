#!/usr/bin/env python3
import http.server, sys, json, base64, hmac, hashlib, sqlite3, os, urllib.parse, time

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 7082
ROOM_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(ROOM_DIR, "boundary.db")
FLAG = "THM{jwt_none_byp4ss}"
FAKE_FLAG = "THM{fake_jwt_none}"
SECRET = b"shadow123"  # تم تسريبه في ملف robots.txt أو debug

# إعداد قاعدة بيانات
conn = sqlite3.connect(DB_PATH)
conn.execute("CREATE TABLE IF NOT EXISTS secrets (id INTEGER, data TEXT)")
conn.execute("INSERT OR IGNORE INTO secrets VALUES (1, ?)", (FLAG,))
conn.execute("CREATE TABLE IF NOT EXISTS users (username TEXT, role TEXT)")
conn.execute("INSERT OR IGNORE INTO users VALUES ('admin', 'admin')")
conn.commit()
conn.close()

# ========== JWT Functions (مكتبة مصغرة) ==========
def b64url_encode(data):
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode()

def b64url_decode(data):
    padding = 4 - len(data) % 4
    if padding != 4:
        data += '=' * padding
    return base64.urlsafe_b64decode(data)

def jwt_create(payload, secret=None, alg="HS256"):
    header = {"alg": alg, "typ": "JWT"}
    header_b64 = b64url_encode(json.dumps(header, separators=(",", ":")).encode())
    payload_b64 = b64url_encode(json.dumps(payload, separators=(",", ":")).encode())
    if alg == "none":
        return f"{header_b64}.{payload_b64}."
    sig = hmac.new(secret, f"{header_b64}.{payload_b64}".encode(), hashlib.sha256).digest()
    return f"{header_b64}.{payload_b64}.{b64url_encode(sig)}"

def jwt_verify(token, secret):
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        header = json.loads(b64url_decode(parts[0]))
        alg = header.get("alg", "HS256")
        if alg == "none":
            # قبول none – ثغرة حقيقية!
            return json.loads(b64url_decode(parts[1]))
        # تحقق من التوقيع
        expected_sig = b64url_encode(hmac.new(secret, f"{parts[0]}.{parts[1]}".encode(), hashlib.sha256).digest())
        if parts[2] != expected_sig:
            return None
        return json.loads(b64url_decode(parts[1]))
    except:
        return None

# ========== HTML Templates ==========
LOGIN_PAGE = """<html><head><title>JWT Auth</title>
<style>body{background:#0a0c10;display:flex;justify-content:center;align-items:center;height:100vh;font-family:'Segoe UI',sans-serif;}
.box{background:#1a1c2b;padding:2rem;border-radius:12px;box-shadow:0 0 20px rgba(0,255,0,0.2);}
h2{color:#00ff00;} input{width:100%;padding:10px;margin:8px 0;background:#0d0f1a;border:1px solid #333;color:white;border-radius:5px;}
input[type=submit]{background:#00aa00;border:none;cursor:pointer;font-weight:bold;}
</style></head><body><div class="box"><h2>JWT Boundary</h2>
<form method="POST" action="/login">
<input name="username" placeholder="Username"><br>
<input name="password" placeholder="Password"><br>
<input type="submit" value="Sign In"></form></div></body></html>"""

DASHBOARD = """<html><head><title>Admin Area</title>
<style>body{background:#0a0c10;color:#c9d1d9;font-family:'Segoe UI',sans-serif;padding:2rem;}
h2{color:#00ff00;} .card{background:#1a1c2b;padding:1rem;border-radius:8px;margin:1rem 0;}
input,button{padding:8px;border-radius:5px;} input{background:#0d0f1a;border:1px solid #333;color:white;}
button{background:#00aa00;border:none;color:white;font-weight:bold;margin-left:5px;cursor:pointer;}
.result{background:#0d0f1a;padding:1rem;margin-top:1rem;border-radius:5px;}</style></head><body>
<h2>Admin Dashboard</h2><div class="card"><h3>Secret Lookup</h3>
<form method="GET" action="/admin/lookup"><input name="id" placeholder="ID"><button>Search</button></form>
<div class="result">%RESULT%</div></div><a href="/logout" style="color:#00ff00;">Logout</a></body></html>"""

class JWTHandler(http.server.BaseHTTPRequestHandler):
    def handle_one_request(self):
        try:
            super().handle_one_request()
        except (ConnectionResetError, BrokenPipeError):
            pass

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        qs = urllib.parse.parse_qs(parsed.query)
        token = self._get_token()

        if path == "/":
            self._serve_html(LOGIN_PAGE)
        elif path == "/robots.txt":
            self._serve_text("User-agent: *\nDisallow: /debug/\nDisallow: /admin/\n# Internal note: secret for JWT is 'shadow123'")
        elif path == "/debug/flag":
            self._serve_text(f"DEBUG FLAG: {FAKE_FLAG}")
        elif path == "/debug/config":
            self._serve_text(f"JWT_ALG=none\nJWT_SECRET=shadow123\nDB_PATH={DB_PATH}")
        elif path == "/admin":
            payload = jwt_verify(token, SECRET) if token else None
            if not payload or payload.get("role") != "admin":
                self.send_error(403, "Admin access only")
                return
            self._serve_html(DASHBOARD.replace("%RESULT%", ""))
        elif path == "/admin/lookup":
            payload = jwt_verify(token, SECRET) if token else None
            if not payload or payload.get("role") != "admin":
                self.send_error(403)
                return
            uid = qs.get('id', [''])[0]
            if uid:
                conn = sqlite3.connect(DB_PATH)
                try:
                    row = conn.execute(f"SELECT data FROM secrets WHERE id = {uid}").fetchone()
                    result = f"Secret: {row[0]}" if row else "Not found"
                except Exception as e:
                    result = f"Error: {e}"
                finally:
                    conn.close()
            else:
                result = "Enter ID"
            self._serve_html(DASHBOARD.replace("%RESULT%", result))
        elif path == "/logout":
            self.send_response(302)
            self.send_header("Set-Cookie", "token=; expires=Thu, 01 Jan 1970 00:00:00 GMT")
            self.send_header("Location", "/")
            self.end_headers()
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path == "/login":
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode()
            data = urllib.parse.parse_qs(body)
            user = data.get('username', [''])[0]
            pwd = data.get('password', [''])[0]
            if user == 'guest' and pwd == 'guest':
                payload = {"user": "guest", "role": "user", "scope": "read", "iat": int(time.time())}
                token = jwt_create(payload, SECRET, alg="HS256")
                self.send_response(302)
                self.send_header("Set-Cookie", f"token={token}; Path=/")
                self.send_header("Location", "/")
                self.end_headers()
            else:
                self.send_error(403, "Invalid credentials")
        else:
            self.send_error(404)

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

    def _serve_text(self, text):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(text.encode())

    def log_message(self, format, *args):
        pass

if __name__ == "__main__":
    server = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), JWTHandler)
    print("Server active", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
