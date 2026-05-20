#!/usr/bin/env python3
import http.server, sys, json, os, urllib.parse, uuid, time, sqlite3, base64, hmac, hashlib, socket, threading

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 13001
ROOM_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(ROOM_DIR, "blackbox.db")
SECRET = b"portal_jwt_secret"
FLAG_FAKE = "SHINIGAMI{fake_portal_2026}"

def b64e(d): return base64.urlsafe_b64encode(d).rstrip(b'=').decode()
def b64d(d):
    d += '=' * (4 - len(d) % 4)
    return base64.urlsafe_b64decode(d)
def jwt_create(payload, secret=SECRET, kid="portal_key", alg="HS256"):
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
        return json.loads(b64d(p)) if sig == expected else None
    except: return None

STATIC_HTML = """<!DOCTYPE html><html><head><title>Corp Portal</title>
<style>body{background:#0a0c10;color:#c9d1d9;font-family:'Segoe UI',sans-serif;text-align:center;padding:4rem;}
h1{color:#f0883e;}</style></head><body><h1>Welcome to the Corporate Portal</h1><p>System status: operational.</p>
</body></html>"""

ROBOTS_TXT = ""

CONFIG = json.dumps({
    "jwt_secret": "portal_jwt_secret",
    "internal_services": ["auth:13002", "users:13003", "billing:13004"],
    "note": "Legacy system available on request"
})

DEBUG_PAGE = json.dumps({"status":"ok","fake_flag":FLAG_FAKE})

sessions = {}
rate_limit = {}

class ProxyHandler(http.server.BaseHTTPRequestHandler):
    def handle_one_request(self):
        try: super().handle_one_request()
        except (ConnectionResetError, BrokenPipeError): pass

    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path
        ua = self.headers.get('User-Agent','')
        client_ip = self.client_address[0]
        now = time.time()
        rate_limit.setdefault(client_ip, []).append(now)
        rate_limit[client_ip] = [t for t in rate_limit[client_ip] if now - t < 10]
        if len(rate_limit[client_ip]) > 30:
            self.send_error(429, "Rate limit exceeded"); return

        # Behavior changes based on User-Agent
        if "InternalBot" in ua:
            if path == "/": self._serve_text("Internal status: OK. Services: /auth, /users, /billing, /legacy")
            elif path == "/config": self._serve_json(CONFIG)
            else: self.send_error(404)
        else:
            if path == "/": self._serve_html(STATIC_HTML)
            elif path == "/robots.txt": self._serve_text(ROBOTS_TXT)
            elif path == "/debug": self._serve_json(DEBUG_PAGE)
            elif path == "/config": self._serve_json(CONFIG)
            elif path == "/login":
                if ua == "MobileApp/1.0":
                    self._serve_text("Login via API only")
                else:
                    self._serve_html("<h2>Login</h2><form method='POST' action='/login'><input name='username'><input type='password' name='password'><input type='submit'></form>")
            elif path == "/fetch":
                url = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query).get('url', [None])[0]
                if not url: self.send_error(400); return
                # Filter bypass only blocks localhost/127.0.0.1, but allows decimal/hex
                parsed = urllib.parse.urlparse(url)
                if parsed.hostname in ['127.0.0.1', 'localhost']:
                    self._serve_text("Blocked: internal host"); return
                # Simulate SSRF (for internal pivot)
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(5)
                    host = parsed.hostname; port = parsed.port or 80
                    s.connect((host, port))
                    req = f"GET {parsed.path}?{parsed.query} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"
                    s.sendall(req.encode())
                    resp = b""
                    while True:
                        chunk = s.recv(4096)
                        if not chunk: break
                        resp += chunk
                    s.close()
                    body = resp.split(b'\r\n\r\n', 1)[1] if b'\r\n\r\n' in resp else b""
                    self._serve_text(body.decode(errors='ignore'))
                except Exception as e:
                    self._serve_text(f"Error: {e}")
            elif path == "/dashboard":
                # Only accessible if JWT admin token
                auth = self.headers.get("Authorization","")
                token = auth.replace("Bearer ","") if auth.startswith("Bearer ") else None
                payload = jwt_verify(token) if token else None
                if not payload or payload.get("role")!="admin":
                    self.send_error(403); return
                self._serve_html("<h2>Admin Dashboard</h2><p>Flag piece 1: SHINIGAMI{blackbox_</p><p>Other services: /auth, /users, /billing</p>")
            else: self.send_error(404)

    def do_POST(self):
        if self.path == "/login":
            content_length = int(self.headers.get('Content-Length',0))
            body = self.rfile.read(content_length).decode()
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
            else: self.send_error(403)

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
