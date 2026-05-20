#!/usr/bin/env python3
import http.server, sys, json, urllib.parse, time, uuid, sqlite3, os, threading

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8601
ROOM_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(ROOM_DIR, "race.db")
FLAG_REAL = "THM{r4c3_4nd_id0r_ch4in}"
FLAG_FAKE = "THM{fake_race_admin}"

# ---------- إعداد قاعدة البيانات ----------
conn = sqlite3.connect(DB_PATH)
conn.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT, flag TEXT)")
conn.execute("INSERT OR IGNORE INTO users VALUES (1, 'admin', 'admin123', 'admin', ?)", (FLAG_FAKE,))
conn.execute("INSERT OR IGNORE INTO users VALUES (2, 'guest', 'guest', 'user', '')")
conn.execute("INSERT OR IGNORE INTO users VALUES (3, 'flag_holder', 'complexpw', 'user', ?)", (FLAG_REAL,))
conn.commit()
conn.close()

# ---------- تخزين الجلسات (بسيط) ----------
sessions = {}
sessions_lock = threading.Lock()

# ---------- HTML ----------
INDEX_HTML = """<!DOCTYPE html>
<html><head><title>RaceCorp Portal</title>
<style>body{background:#0a0c10;color:#c9d1d9;font-family:'Segoe UI',sans-serif;display:flex;justify-content:center;align-items:center;height:100vh;margin:0;}
.box{background:#1a1c2b;padding:2rem;border-radius:12px;} h2{color:#e53170;}
input{width:100%;padding:10px;margin:8px 0;background:#0d0f1a;border:1px solid #333;color:white;border-radius:5px;}
input[type=submit]{background:#e53170;border:none;cursor:pointer;font-weight:bold;}
</style></head><body><div class="box"><h2>Employee Portal</h2>
<form method="POST" action="/login"><input name="username" placeholder="Username"><br>
<input type="password" name="password" placeholder="Password"><br>
<input type="submit" value="Log In"></form>
<!-- Timing debug: response header X-Process-Time indicates server processing time -->
</div></body></html>"""

DASHBOARD = """<!DOCTYPE html>
<html><head><title>Dashboard</title>
<style>body{background:#0a0c10;color:#c9d1d9;font-family:'Segoe UI',sans-serif;padding:2rem;}
h2{color:#00ff00;} .card{background:#1a1c2b;padding:1rem;border-radius:8px;margin:1rem 0;}
a{color:#58a6ff;}</style></head><body>
<h2>Welcome, {username}</h2>
<div class="card"><p>Your role: {role}</p></div>
<div class="card"><p><a href="/admin/profile?user_id={user_id}">View Profile</a></p></div>
<a href="/logout">Logout</a></body></html>"""

PROFILE_PAGE = """<!DOCTYPE html>
<html><head><title>Profile</title>
<style>body{background:#0a0c10;color:#c9d1d9;font-family:'Segoe UI',sans-serif;padding:2rem;}
pre{background:#0d0f1a;padding:1rem;border-radius:5px;}</style></head><body>
<h2>User Profile</h2>
<pre>{profile_data}</pre>
<a href="/dashboard">Back</a></body></html>"""

ROBOTS_TXT = """User-agent: *
Disallow: /debug
"""

DEBUG_PAGE = json.dumps({"status":"debug","processing_delay":"0.5s","race_hint":True,"fake_flag":FLAG_FAKE})

class RaceHandler(http.server.BaseHTTPRequestHandler):
    def handle_one_request(self):
        try:
            super().handle_one_request()
        except (ConnectionResetError, BrokenPipeError):
            pass

    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path
        qs = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        session_id = self._get_cookie('session')

        if path == "/":
            self._serve_html(INDEX_HTML)
        elif path == "/robots.txt":
            self._serve_text(ROBOTS_TXT)
        elif path == "/debug":
            self._serve_json(DEBUG_PAGE)
        elif path == "/dashboard":
            user = self._get_user(session_id) if session_id else None
            if not user:
                self.send_error(403, "Login required"); return
            page = DASHBOARD.replace("{username}", user["username"]).replace("{role}", user["role"]).replace("{user_id}", str(user["id"]))
            self._serve_html(page)
        elif path == "/admin/profile":
            user = self._get_user(session_id) if session_id else None
            if not user:
                self.send_error(403); return
            target_id = qs.get('user_id', [str(user["id"])])[0]
            # ---------- IDOR: لا تحقق من صلاحية المستخدم ----------
            conn = sqlite3.connect(DB_PATH)
            row = conn.execute("SELECT username, role, flag FROM users WHERE id = ?", (target_id,)).fetchone()
            conn.close()
            if not row:
                self.send_error(404, "User not found")
                return
            profile_text = f"Username: {row[0]}\nRole: {row[1]}"
            if row[2]:
                profile_text += f"\nFlag: {row[2]}"
            self._serve_html(PROFILE_PAGE.replace("{profile_data}", profile_text))
        elif path == "/logout":
            self.send_response(302)
            self.send_header("Set-Cookie", "session=; expires=Thu, 01 Jan 1970 00:00:00 GMT")
            self.send_header("Location", "/")
            self.end_headers()
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path == "/login":
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode()
            data = urllib.parse.parse_qs(body)
            username = data.get('username', [''])[0]
            password = data.get('password', [''])[0]

            # ========== الثغرة: جلسة تُنشأ قبل التحقق ==========
            new_sid = uuid.uuid4().hex
            # 1. إنشاء جلسة مؤقتة على الفور
            with sessions_lock:
                sessions[new_sid] = {"username": username, "role": "user", "id": None}  # id غير معروف بعد

            # 2. إرسال الكعكة فوراً (قبل التحقق)
            self.send_response(302)
            self.send_header("Set-Cookie", f"session={new_sid}; Path=/")
            self.send_header("Location", "/dashboard")
            self.end_headers()

            # 3. تأخير لمحاكاة تحقق بطيء (نافذة السباق)
            time.sleep(0.5)  # 500ms

            # 4. التحقق من كلمة المرور
            conn = sqlite3.connect(DB_PATH)
            row = conn.execute("SELECT id, username, role FROM users WHERE username=? AND password=?", (username, password)).fetchone()
            conn.close()

            if row:
                # تصحيح الجلسة
                with sessions_lock:
                    sessions[new_sid] = {"username": row[1], "role": row[2], "id": row[0]}
            else:
                # حذف الجلسة (لكن النافذة السابقة قد تكون سُمِحت)
                with sessions_lock:
                    sessions.pop(new_sid, None)
        else:
            self.send_error(404)

    def _get_cookie(self, key):
        cookie_str = self.headers.get('Cookie', '')
        if f'{key}=' in cookie_str:
            return cookie_str.split(f'{key}=')[1].split(';')[0]
        return None

    def _get_user(self, session_id):
        with sessions_lock:
            return sessions.get(session_id)

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

    def _serve_json(self, data):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def log_message(self, format, *args):
        pass

if __name__ == "__main__":
    server = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), RaceHandler)
    print(f"Race server on {PORT}", flush=True)
    server.serve_forever()
