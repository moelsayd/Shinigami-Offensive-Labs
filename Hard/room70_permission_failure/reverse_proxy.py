#!/usr/bin/env python3
import http.server, sys, json, os, urllib.parse, uuid, time, sqlite3, base64, hmac, hashlib, socket, re

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 11001
ROOM_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(ROOM_DIR, "enterprise.db")
SECRET = b"secret123"  # ضعيف
FLAG_FAKE = "THM{fake_main_portal}"

def b64e(d): return base64.urlsafe_b64encode(d).rstrip(b'=').decode()
def b64d(d):
    d += '=' * (4 - len(d) % 4)
    return base64.urlsafe_b64decode(d)
def jwt_create(payload, secret=SECRET, kid="main_key", alg="HS256"):
    header = {"alg":alg,"typ":"JWT","kid":kid}
    h = b64e(json.dumps(header).encode())
    p = b64e(json.dumps(payload).encode())
    if alg == "none": return f"{h}.{p}."
    sig = b64e(hmac.new(secret, f"{h}.{p}".encode(), hashlib.sha256).digest())
    return f"{h}.{p}.{sig}"
def jwt_verify(token, secret=SECRET):
    try:
        h, p, sig = token.split(".")
        header = json.loads(b64d(h))
        if header.get("alg") == "none": return json.loads(b64d(p))
        expected = b64e(hmac.new(secret, f"{h}.{p}".encode(), hashlib.sha256).digest())
        if sig != expected: return None
        return json.loads(b64d(p))
    except: return None

LOGIN_HTML = """<!DOCTYPE html>
<html><head><title>Enterprise Portal</title>
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
a{color:#58a6ff;}</style></head><body>
<h2>Dashboard</h2>
<div class="card"><p>Welcome {user}, your role is {role}.</p></div>
<div class="card"><h3>Services</h3>
<p><a href="/service-a">Service A (User Upgrade)</a></p>
<p><a href="/service-b">Service B (Admin Panel)</a></p>
</div>
<a href="/logout">Logout</a></body></html>"""

ROBOTS_TXT = """User-agent: *
Disallow: /debug
Disallow: /config
"""

DEBUG_PAGE = json.dumps({"status":"ok","fake_flag":FLAG_FAKE})

sessions = {}
rate_limit = {}

class ProxyHandler(http.server.BaseHTTPRequestHandler):
    def handle_one_request(self):
        try: super().handle_one_request()
        except (ConnectionResetError, BrokenPipeError): pass

    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path
        client_ip = self.client_address[0]
        now = time.time()
        rate_limit.setdefault(client_ip, []).append(now)
        rate_limit[client_ip] = [t for t in rate_limit[client_ip] if now - t < 10]
        if len(rate_limit[client_ip]) > 30:
            self.send_error(429, "Rate limit exceeded"); return

        if path == "/": self._serve_html(LOGIN_HTML)
        elif path == "/robots.txt": self._serve_text(ROBOTS_TXT)
        elif path == "/debug": self._serve_json(DEBUG_PAGE)
        elif path == "/dashboard":
            sid = self._get_cookie('session'); user = sessions.get(sid)
            if not user: self.send_error(403); return
            conn = sqlite3.connect(DB_PATH)
            row = conn.execute("SELECT username, role FROM users WHERE id=?", (user["id"],)).fetchone()
            conn.close()
            self._serve_html(DASHBOARD.replace("{user}",row[0]).replace("{role}",row[1]))
        elif path == "/service-a":
            # إعادة توجيه إلى الخدمة الداخلية A
            self._proxy_request("127.0.0.1", 11022, path)
        elif path == "/service-b":
            self._proxy_request("127.0.0.1", 11033, path)
        elif path == "/logout":
            self.send_response(302)
            self.send_header("Set-Cookie","session=; expires=Thu, 01 Jan 1970 00:00:00 GMT")
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
                sid = uuid.uuid4().hex; sessions[sid] = {"id":row[0],"username":row[1]}
                token = jwt_create({"user":row[1],"role":"user","id":row[0],"iat":int(time.time())})
                self.send_response(302)
                self.send_header("Set-Cookie", f"token={token}; Path=/")
                self.send_header("Location", "/dashboard"); self.end_headers()
            else: self.send_error(403, "Invalid credentials")
        elif path == "/service-a":
            self._proxy_post("127.0.0.1", 11022, path, body)
        else:
            self.send_error(404)

    def _proxy_request(self, host, port, path):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(5)
            s.connect((host, port))
            req = f"GET {path} HTTP/1.1\r\nHost: {host}:{port}\r\nCookie: {self.headers.get('Cookie','')}\r\nAuthorization: {self.headers.get('Authorization','')}\r\n\r\n"
            s.sendall(req.encode())
            resp = b""
            while True:
                chunk = s.recv(4096)
                if not chunk: break
                resp += chunk
            s.close()
            self.send_response(200)
            self.end_headers()
            self.wfile.write(resp)
        except Exception as e:
            self.send_error(502, str(e))

    def _proxy_post(self, host, port, path, body):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(5)
            s.connect((host, port))
            req = f"POST {path} HTTP/1.1\r\nHost: {host}:{port}\r\nContent-Length: {len(body)}\r\nCookie: {self.headers.get('Cookie','')}\r\n\r\n{body}"
            s.sendall(req.encode())
            resp = b""
            while True:
                chunk = s.recv(4096)
                if not chunk: break
                resp += chunk
            s.close()
            self.send_response(200)
            self.end_headers()
            self.wfile.write(resp)
        except Exception as e:
            self.send_error(502, str(e))

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
    server = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), ProxyHandler)
    print(f"Proxy on {PORT}", flush=True)
    server.serve_forever()
