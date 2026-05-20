#!/usr/bin/env python3
import http.server, sys, json, os, urllib.parse, uuid, time, sqlite3, threading

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 9501
ROOM_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(ROOM_DIR, "logic.db")
FLAG_FAKE = "THM{fake_logic_web}"
API_KEY = "xxe_api_key_123"

# قاعدة بيانات
conn = sqlite3.connect(DB_PATH)
conn.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT, balance INTEGER)")
conn.execute("INSERT OR IGNORE INTO users VALUES (1, 'admin', 'admin123', 'user', 0)")
conn.execute("INSERT OR IGNORE INTO users VALUES (2, 'guest', 'guest', 'user', 100)")
conn.commit()
conn.close()

LOGIN_HTML = """<!DOCTYPE html>
<html><head><title>BizLogic Corp</title>
<style>body{background:#0a0c10;color:#c9d1d9;font-family:'Segoe UI',sans-serif;display:flex;justify-content:center;align-items:center;height:100vh;margin:0;}
.box{background:#1a1c2b;padding:2rem;border-radius:12px;} h2{color:#e53170;}
input{width:100%;padding:10px;margin:8px 0;background:#0d0f1a;border:1px solid #333;color:white;border-radius:5px;}
input[type=submit]{background:#e53170;border:none;cursor:pointer;font-weight:bold;}
</style></head><body><div class="box"><h2>Login</h2>
<form method="POST" action="/login"><input name="username" placeholder="Username"><br>
<input type="password" name="password" placeholder="Password"><br>
<input type="submit" value="Log In"></form>
<!-- Default guest:guest -->
</div></body></html>"""

DASHBOARD = """<html><head><title>Dashboard</title>
<style>body{background:#0a0c10;color:#c9d1d9;font-family:'Segoe UI',sans-serif;padding:2rem;}
h2{color:#00ff00;} .card{background:#1a1c2b;padding:1rem;border-radius:8px;margin:1rem 0;}
input,button{padding:8px;margin:5px;border-radius:5px;} input{background:#0d0f1a;border:1px solid #333;color:white;}
button{background:#e53170;border:none;color:white;font-weight:bold;cursor:pointer;}
</style></head><body>
<h2>Dashboard</h2><p>Balance: {balance} credits</p>
<div class="card"><h3>Refund</h3>
<form method="POST" action="/refund"><input name="amount" placeholder="Amount"><button>Refund</button></form>
</div>
<div class="card"><h3>Purchase</h3>
<p>Admin API Key: 1000 credits</p>
<form method="POST" action="/purchase"><input type="hidden" name="item" value="admin_key"><button>Buy</button></form>
</div>
<div class="card">{secret}</div>
<a href="/logout">Logout</a></body></html>"""

ROBOTS_TXT = """User-agent: *
Disallow: /config
Disallow: /debug
"""

CONFIG = json.dumps({"api_key": API_KEY, "internal_service": "http://localhost:9502/parse", "note":"XXE service expects XML documents"})

DEBUG_PAGE = json.dumps({"status":"ok","fake_flag":FLAG_FAKE})

sessions = {}

class WebHandler(http.server.BaseHTTPRequestHandler):
    def handle_one_request(self):
        try: super().handle_one_request()
        except (ConnectionResetError, BrokenPipeError): pass

    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path
        sid = self._get_cookie('session')
        user = sessions.get(sid)

        if path == "/": self._serve_html(LOGIN_HTML)
        elif path == "/robots.txt": self._serve_text(ROBOTS_TXT)
        elif path == "/config": self._serve_json(CONFIG)
        elif path == "/debug": self._serve_json(DEBUG_PAGE)
        elif path == "/dashboard":
            if not user: self.send_error(403); return
            conn = sqlite3.connect(DB_PATH)
            row = conn.execute("SELECT username, balance, role FROM users WHERE id=?", (user["id"],)).fetchone()
            conn.close()
            if not row: self.send_error(403); return
            balance = row[1]; secret = ""
            if balance >= 1000: secret = f"API Key: {API_KEY}"
            page = DASHBOARD.replace("{balance}", str(balance)).replace("{secret}", secret)
            self._serve_html(page)
        elif path == "/logout":
            self.send_response(302)
            self.send_header("Set-Cookie","session=; expires=Thu, 01 Jan 1970 00:00:00 GMT")
            self.send_header("Location","/"); self.end_headers()
        else: self.send_error(404)

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length',0))
        body = self.rfile.read(content_length).decode()
        data = urllib.parse.parse_qs(body)
        path = urllib.parse.urlparse(self.path).path

        if path == "/login":
            user = data.get('username',[''])[0]; pwd = data.get('password',[''])[0]
            conn = sqlite3.connect(DB_PATH)
            row = conn.execute("SELECT id, role FROM users WHERE username=? AND password=?", (user,pwd)).fetchone()
            conn.close()
            if row:
                sid = uuid.uuid4().hex; sessions[sid] = {"id":row[0], "role":row[1]}
                self.send_response(302)
                self.send_header("Set-Cookie", f"session={sid}; Path=/")
                self.send_header("Location", "/dashboard"); self.end_headers()
            else: self.send_error(403, "Invalid credentials")
        elif path == "/refund":
            sid = self._get_cookie('session'); user = sessions.get(sid)
            if not user: self.send_error(403); return
            try: amount = int(data.get('amount',['0'])[0])
            except: amount = 0
            # !!! ثغرة منطقية: لا يوجد تحقق من أن المبلغ موجب
            conn = sqlite3.connect(DB_PATH)
            conn.execute("UPDATE users SET balance = balance - ? WHERE id=?", (amount, user["id"]))
            conn.commit()
            new_balance = conn.execute("SELECT balance FROM users WHERE id=?", (user["id"],)).fetchone()[0]
            conn.close()
            self.send_response(302)
            self.send_header("Location", "/dashboard"); self.end_headers()
        elif path == "/purchase":
            sid = self._get_cookie('session'); user = sessions.get(sid)
            if not user: self.send_error(403); return
            item = data.get('item',[''])[0]
            if item == "admin_key":
                conn = sqlite3.connect(DB_PATH)
                balance = conn.execute("SELECT balance FROM users WHERE id=?", (user["id"],)).fetchone()[0]
                if balance >= 1000:
                    conn.execute("UPDATE users SET balance = balance - 1000 WHERE id=?", (user["id"],))
                    conn.commit()
                    conn.close()
                    # إظهار API key في الصفحة التالية
                    self.send_response(302)
                    self.send_header("Location", "/dashboard"); self.end_headers()
                else:
                    conn.close(); self.send_error(403, "Insufficient balance")
            else:
                self.send_error(400)
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
