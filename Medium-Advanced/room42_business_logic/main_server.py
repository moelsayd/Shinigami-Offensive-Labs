#!/usr/bin/env python3
import http.server, sys, json, sqlite3, os, uuid, urllib.parse, time

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 7101
ROOM_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(ROOM_DIR, "business.db")
FLAG_REAL = "THM{bus1n3ss_l0g1c_1d0r}"
FLAG_FAKE = "THM{fake_business_flag}"

LOGIN_HTML = """<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><title>BizLogic Corp</title>
<style>body{background:#0a0c10;color:#c9d1d9;font-family:'Segoe UI',sans-serif;display:flex;justify-content:center;align-items:center;height:100vh;margin:0;}
.box{background:#1a1c2b;padding:2rem;border-radius:12px;box-shadow:0 0 20px rgba(0,255,0,0.2);}
h2{color:#00ff00;} input{width:100%;padding:10px;margin:8px 0;background:#0d0f1a;border:1px solid #333;color:white;border-radius:5px;}
input[type=submit]{background:#00aa00;border:none;cursor:pointer;font-weight:bold;}
</style></head><body><div class="box"><h2>Login</h2>
<form method="POST" action="/login"><input name="username" placeholder="Username"><br>
<input type="password" name="password" placeholder="Password"><br>
<input type="submit" value="Log In"></form>
</div></body></html>"""

UPGRADE_PAGE = """<!DOCTYPE html>
<html><head><title>Upgrade Plan</title>
<style>body{background:#0a0c10;color:#c9d1d9;font-family:'Segoe UI',sans-serif;padding:2rem;}
h2{color:#f0883e;} .card{background:#1a1c2b;padding:1rem;border-radius:8px;margin:1rem 0;}
input,select,button{padding:8px;margin:5px;border-radius:5px;background:#0d0f1a;border:1px solid #333;color:white;}
button{background:#00aa00;border:none;cursor:pointer;}
.result{background:#0d0f1a;padding:1rem;margin-top:1rem;border-radius:5px;}</style></head><body>
<h2>Plan Upgrade</h2><div class="card"><form method="POST" action="/api/upgrade">
<label>Select Plan:</label><select name="plan"><option>free</option><option>premium</option><option>enterprise</option></select><br>
<label>Coupon Code:</label><input name="coupon"><br>
<button>Upgrade</button></form><div class="result">%RESULT%</div>
</div><a href="/logout" style="color:#e53170;">Logout</a></body></html>"""

ROBOTS_TXT = """User-agent: *
Disallow: /admin-panel/
Disallow: /api/
"""

FAKE_ADMIN_PAGE = f"""<html><body><h1>Admin Panel</h1><p>Flag: {FLAG_FAKE}</p></body></html>"""

sessions = {}

class MainHandler(http.server.BaseHTTPRequestHandler):
    def handle_one_request(self):
        try:
            super().handle_one_request()
        except (ConnectionResetError, BrokenPipeError):
            pass

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/":
            self._serve_html(LOGIN_HTML)
        elif path == "/robots.txt":
            self._serve_text(ROBOTS_TXT)
        elif path == "/admin-panel/":
            self._serve_html(FAKE_ADMIN_PAGE)
        elif path == "/upgrade":
            if not self._is_auth():
                self.send_error(403); return
            self._serve_html(UPGRADE_PAGE.replace("%RESULT%", ""))
        elif path == "/logout":
            self._clear_auth()
            self.send_response(302)
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
            conn = sqlite3.connect(DB_PATH)
            row = conn.execute("SELECT id, role FROM users WHERE username=? AND password=?", (user, pwd)).fetchone()
            conn.close()
            if row:
                sid = uuid.uuid4().hex
                sessions[sid] = {"id": row[0], "role": row[1]}
                self.send_response(302)
                self.send_header("Set-Cookie", f"session={sid}; Path=/")
                self.send_header("Location", "/upgrade")
                self.end_headers()
            else:
                self.send_error(403, "Invalid credentials")
        elif self.path == "/api/upgrade":
            if not self._is_auth():
                self.send_error(403); return
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode()
            data = urllib.parse.parse_qs(body)
            plan = data.get('plan', ['free'])[0]
            coupon = data.get('coupon', [''])[0]

            # Business Logic: أي plan يتم قبوله إذا كان الكوبون صحيحًا
            valid_coupons = ["WELCOME50", "UPGRADE2026"]
            if coupon in valid_coupons:
                # التحديث في قاعدة البيانات
                session = self._get_session()
                conn = sqlite3.connect(DB_PATH)
                conn.execute("UPDATE users SET plan=? WHERE id=?", (plan, session["id"]))
                conn.commit()
                # توليد api key فقط لـ enterprise
                if plan == "enterprise":
                    api_key = uuid.uuid4().hex[:16]
                    conn.execute("UPDATE users SET api_key=? WHERE id=?", (api_key, session["id"]))
                    conn.commit()
                    result = f"Upgraded to {plan}. API Key: {api_key}. Internal dashboard at http://localhost:7102/dashboard?key=YOUR_KEY"
                elif plan == "premium":
                    result = f"Upgraded to {plan}. Enjoy new features! (Flag: {FLAG_FAKE})"
                else:
                    result = "Plan updated."
                conn.close()
                self._serve_html(UPGRADE_PAGE.replace("%RESULT%", result))
            else:
                self._serve_html(UPGRADE_PAGE.replace("%RESULT%", "Invalid coupon."))
        else:
            self.send_error(404)

    def _is_auth(self):
        return self._get_session() is not None

    def _get_session(self):
        cookie = self.headers.get('Cookie', '')
        if 'session=' in cookie:
            sid = cookie.split('session=')[1].split(';')[0]
            return sessions.get(sid)
        return None

    def _clear_auth(self):
        self.send_header("Set-Cookie", "session=; expires=Thu, 01 Jan 1970 00:00:00 GMT")

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
    server = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), MainHandler)
    print("Server active", flush=True)
    server.serve_forever()
