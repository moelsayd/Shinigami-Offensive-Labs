#!/usr/bin/env python3
import http.server, sys, json, os, urllib.parse, uuid, time, sqlite3, threading, socket, re

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 10901
ROOM_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(ROOM_DIR, "race.db")
MONITOR_HOST = "127.0.0.1"
MONITOR_PORT = 10922
INTERNAL_WORKER = f"http://{MONITOR_HOST}:10933"
FLAG_FAKE = "THM{fake_web_purchase}"

LOGIN_HTML = """<!DOCTYPE html>
<html><head><title>FinCorp</title>
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
input,button{padding:8px;margin:5px;border-radius:5px;} input{background:#0d0f1a;border:1px solid #333;color:white;}
button{background:#e53170;border:none;color:white;font-weight:bold;cursor:pointer;}
</style></head><body>
<h2>Dashboard</h2><p>Balance: {balance} credits</p>
<div class="card"><h3>Transfer</h3>
<form method="POST" action="/transfer"><input name="to" placeholder="Recipient"><br>
<input name="amount" placeholder="Amount"><br><button>Transfer</button></form>
</div>
<div class="card"><h3>Purchase Premium</h3>
<p>Price: 2000 credits (includes monitoring token)</p>
<form method="POST" action="/purchase"><button>Buy</button></form>
</div>
<div class="card">{secret}</div>
<a href="/logout">Logout</a></body></html>"""

ROBOTS_TXT = """User-agent: *
Disallow: /debug
Disallow: /admin
"""

DEBUG_PAGE = json.dumps({"status":"ok","fake_flag":FLAG_FAKE})

sessions = {}
rate_limit = {}
transfer_lock = threading.Lock()  # لا يعالج السباق بشكل صحيح عن قصد

class WebHandler(http.server.BaseHTTPRequestHandler):
    def handle_one_request(self):
        try: super().handle_one_request()
        except (ConnectionResetError, BrokenPipeError): pass

    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path
        client_ip = self.client_address[0]
        # Rate limiting
        now = time.time()
        rate_limit.setdefault(client_ip, []).append(now)
        rate_limit[client_ip] = [t for t in rate_limit[client_ip] if now - t < 10]
        if len(rate_limit[client_ip]) > 20:
            self.send_error(429, "Rate limit exceeded"); return

        if path == "/": self._serve_html(LOGIN_HTML)
        elif path == "/robots.txt": self._serve_text(ROBOTS_TXT)
        elif path == "/debug": self._serve_json(DEBUG_PAGE)
        elif path == "/dashboard":
            sid = self._get_cookie('session'); user = sessions.get(sid)
            if not user: self.send_error(403); return
            conn = sqlite3.connect(DB_PATH)
            balance = conn.execute("SELECT balance FROM users WHERE id=?", (user["id"],)).fetchone()[0]
            conn.close()
            secret = ""
            if balance >= 2000:
                secret = f"<p><b>Monitoring Token:</b> monitor_token_456</p>"
            self._serve_html(DASHBOARD.replace("{balance}", str(balance)).replace("{secret}", secret))
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
            row = conn.execute("SELECT id, username FROM users WHERE username=? AND password=?", (user,pwd)).fetchone()
            conn.close()
            if row:
                sid = uuid.uuid4().hex; sessions[sid] = {"id":row[0],"username":row[1]}
                self.send_response(302)
                self.send_header("Set-Cookie", f"session={sid}; Path=/")
                self.send_header("Location", "/dashboard"); self.end_headers()
            else: self.send_error(403, "Invalid credentials")
        elif path == "/transfer":
            sid = self._get_cookie('session'); user = sessions.get(sid)
            if not user: self.send_error(403); return
            to = data.get('to',[''])[0]; amount = int(data.get('amount',['0'])[0])
            # !!! ثغرة منطقية: مبلغ سالب يزيد الرصيد (Business Logic)
            # !!! ثغرة سباق: التحقق من الرصيد خارج القفل
            conn = sqlite3.connect(DB_PATH)
            balance = conn.execute("SELECT balance FROM users WHERE id=?", (user["id"],)).fetchone()[0]
            if amount > 0 and balance < amount:
                conn.close(); self.send_error(403, "Insufficient balance"); return
            # عملية غير ذرية: فجوة زمنية بين القراءة والكتابة
            time.sleep(0.5)  # نافذة السباق
            conn.execute("UPDATE users SET balance = balance - ? WHERE id=?", (amount, user["id"]))
            conn.commit()
            new_balance = conn.execute("SELECT balance FROM users WHERE id=?", (user["id"],)).fetchone()[0]
            conn.close()
            self.send_response(302)
            self.send_header("Location", "/dashboard"); self.end_headers()
        elif path == "/purchase":
            sid = self._get_cookie('session'); user = sessions.get(sid)
            if not user: self.send_error(403); return
            conn = sqlite3.connect(DB_PATH)
            balance = conn.execute("SELECT balance FROM users WHERE id=?", (user["id"],)).fetchone()[0]
            if balance >= 2000:
                conn.execute("UPDATE users SET balance = balance - 2000 WHERE id=?", (user["id"],))
                conn.commit()
                conn.close()
                self._serve_text(f"Purchase successful! Monitoring token: monitor_token_456 (use at port 10922)")
            else:
                conn.close(); self.send_error(403, "Insufficient balance")
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
