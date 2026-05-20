#!/usr/bin/env python3
import http.server, sys, json, base64, hmac, hashlib, os, urllib.parse, time, sqlite3, re

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8902
ROOM_DIR = os.path.dirname(os.path.abspath(__file__))
SECRET = b"neo_internal_key"  # مسرب في JS
DB_PATH = os.path.join(ROOM_DIR, "exam.db")
FLAG_REAL = "THM{medium_plus_chain_complete}"
FLAG_FAKE = "THM{fake_api_debug}"

# قاعدة بيانات
conn = sqlite3.connect(DB_PATH)
conn.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, role TEXT, secret TEXT, ssh_creds TEXT)")
conn.execute("INSERT OR IGNORE INTO users VALUES (1, 'admin', 'admin', 'THM{fake_admin_secret}', '')")
conn.execute("INSERT OR IGNORE INTO users VALUES (2, 'dev', 'user', '', '')")
conn.execute("INSERT OR IGNORE INTO users VALUES (3, 'flagholder', 'user', '"+FLAG_REAL+"', 'operator:0p3r4t0rP@ss')")
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

# HTML
CONSOLE_HTML = """<!DOCTYPE html>
<html><head><title>Internal Console</title>
<style>body{background:#0a0c10;color:#c9d1d9;font-family:'Segoe UI',sans-serif;padding:2rem;}
h2{color:#00ff00;} .card{background:#1a1c2b;padding:1rem;border-radius:8px;margin:1rem 0;}
input,button{padding:8px;border-radius:5px;margin:5px;} input{background:#0d0f1a;border:1px solid #333;color:white;}
button{background:#00aa00;border:none;font-weight:bold;color:white;cursor:pointer;}
</style></head><body>
<h2>Internal Console</h2>
<div class="card"><p>Files available: /backup/system.old, /config/dev.env</p></div>
<div class="card"><h3>User Lookup</h3>
<form method="GET" action="/api/v2/user"><input name="id" placeholder="User ID"><button>Search</button></form>
<div>%RESULT%</div>
</div></body></html>"""

ROBOTS_TXT = """User-agent: *
Disallow: /api/
Disallow: /internal/
"""

BACKUP_SYSTEM = """# Old system backup
JWT_SECRET=neo_internal_key
API_ENDPOINT=http://localhost:8902
ADMIN_HEADER=X-API-Key
"""

DEV_ENV = """DB_USER=neo_admin
DB_PASS=neo_2025!
LEGACY_FLAG_PATH=/api/v1/legacy/flag
SSH_PORT=8903
"""

class APIHandler(http.server.BaseHTTPRequestHandler):
    def handle_one_request(self):
        try: super().handle_one_request()
        except: pass

    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path
        qs = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        api_key = self.headers.get("X-API-Key")

        if path == "/robots.txt": self._serve_text(ROBOTS_TXT)
        elif path == "/debug": self._serve_json({"status":"ok","fake_flag":FLAG_FAKE})
        elif path == "/internal/console":
            if api_key != "neo_internal_key": self.send_error(403); return
            uid = qs.get('id',[None])[0]
            if uid:
                conn = sqlite3.connect(DB_PATH)
                try:
                    query = f"SELECT username, role FROM users WHERE id = {uid}"
                    row = conn.execute(query).fetchone()
                    result = f"User: {row[0]}, Role: {row[1]}" if row else "Not found"
                except Exception as e: result = f"Error: {e}"
                finally: conn.close()
            else: result = "Enter ID"
            self._serve_html(CONSOLE_HTML.replace("%RESULT%", result))
        elif path == "/config/dev.env": self._serve_text(DEV_ENV)
        elif path == "/backup/system.old": self._serve_text(BACKUP_SYSTEM)
        elif path == "/api/v1/legacy/flag":
            if self.headers.get("X-Debug-User") == "neo_admin":
                self._serve_text(f"Flag: {FLAG_REAL}\n")
            else: self.send_error(403, "Forbidden")
        elif path == "/api/v2/user":
            if api_key != "neo_internal_key": self.send_error(403); return
            uid = qs.get('id',[None])[0]
            if not uid: self.send_error(400); return
            conn = sqlite3.connect(DB_PATH)
            # SQLi time-based هنا
            try:
                query = f"SELECT username, role, secret, ssh_creds FROM users WHERE id = {uid}"
                row = conn.execute(query).fetchone()
                if row:
                    data = {"username":row[0],"role":row[1]}
                    if row[2]: data["secret"] = row[2]
                    if row[3]: data["ssh_creds"] = row[3]
                    self._serve_json(data)
                else: self._serve_json({"status":"ok"})
            except Exception as e: self._serve_json({"status":"ok"})
            finally: conn.close()
        else: self.send_error(404)

    def _serve_html(self, html):
        self.send_response(200); self.send_header("Content-type","text/html"); self.end_headers(); self.wfile.write(html.encode())
    def _serve_text(self, text):
        self.send_response(200); self.send_header("Content-type","text/plain"); self.end_headers(); self.wfile.write(text.encode())
    def _serve_json(self, data):
        self.send_response(200); self.send_header("Content-type","application/json"); self.end_headers(); self.wfile.write(json.dumps(data).encode())
    def log_message(self, format, *args): pass

if __name__ == "__main__":
    server = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), APIHandler)
    print(f"API on {PORT}", flush=True)
    server.serve_forever()
