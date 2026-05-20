#!/usr/bin/env python3
import http.server, sys, json, os, urllib.parse, uuid, time, sqlite3, threading, re

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 9701
ROOM_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(ROOM_DIR, "uploads")
DB_PATH = os.path.join(ROOM_DIR, "race.db")
os.makedirs(UPLOAD_DIR, exist_ok=True)
FLAG_FAKE = "THM{fake_upload_web}"
SECRET_KEY = b"upload_secret_key"

# قاعدة بيانات
conn = sqlite3.connect(DB_PATH)
conn.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT)")
conn.execute("INSERT OR IGNORE INTO users VALUES (1, 'admin', 'admin123', 'admin')")
conn.execute("INSERT OR IGNORE INTO users VALUES (2, 'guest', 'guest', 'user')")
conn.execute("CREATE TABLE IF NOT EXISTS files (id INTEGER PRIMARY KEY, original_name TEXT, stored_name TEXT, uploader TEXT)")
conn.commit()
conn.close()

def is_image(filename):
    return filename.lower().endswith(('.png','.jpg','.jpeg','.gif'))

LOGIN_HTML = """<!DOCTYPE html>
<html><head><title>FileVault</title>
<style>body{background:#0a0c10;color:#c9d1d9;font-family:'Segoe UI',sans-serif;display:flex;justify-content:center;align-items:center;height:100vh;margin:0;}
.box{background:#1a1c2b;padding:2rem;border-radius:12px;} h2{color:#e53170;}
input{width:100%;padding:10px;margin:8px 0;background:#0d0f1a;border:1px solid #333;color:white;border-radius:5px;}
input[type=submit]{background:#e53170;border:none;cursor:pointer;font-weight:bold;}
</style></head><body><div class="box"><h2>Login</h2>
<form method="POST" action="/login"><input name="username" placeholder="Username"><br>
<input type="password" name="password" placeholder="Password"><br>
<input type="submit" value="Log In"></form>
<!-- guest:guest -->
</div></body></html>"""

DASHBOARD = """<html><head><title>Dashboard</title>
<style>body{background:#0a0c10;color:#c9d1d9;font-family:'Segoe UI',sans-serif;padding:2rem;}
h2{color:#00ff00;} .card{background:#1a1c2b;padding:1rem;border-radius:8px;margin:1rem 0;}
input,button{padding:8px;margin:5px;border-radius:5px;} input{background:#0d0f1a;border:1px solid #333;color:white;}
button{background:#e53170;border:none;color:white;font-weight:bold;cursor:pointer;}
</style></head><body>
<h2>Dashboard</h2>
<div class="card"><h3>Upload File</h3>
<form id="uploadForm" action="/api/upload" method="post" enctype="multipart/form-data">
<input type="file" name="file" id="fileInput"><br>
<button type="button" onclick="checkFile()">Upload</button>
</form>
<p id="error" style="color:red;"></p>
<script>
function checkFile() {
    const file = document.getElementById('fileInput').files[0];
    if (file && !file.name.match(/\\.(png|jpg|jpeg|gif)$/i)) {
        document.getElementById('error').innerText = "Only images allowed!";
        return;
    }
    document.getElementById('error').innerText = "";
    document.getElementById('uploadForm').submit();
}
</script>
</div>
<div class="card"><h3>My Files</h3>
<ul>%FILES%</ul>
</div>
<div class="card"><h3>Share with Admin</h3>
<form method="POST" action="/share"><input name="file_url" placeholder="http://..."><button>Share</button></form>
<p style="font-size:0.8rem;color:#8b949e;">Admin visits shared links automatically</p>
</div>
<a href="/logout">Logout</a></body></html>"""

ROBOTS_TXT = """User-agent: *
Disallow: /config/
Disallow: /debug
Disallow: /admin
"""

CONFIG = json.dumps({
    "backend_api": "/api/upload",
    "note": "Frontend checks file extension only, backend trusts it"
})

DEBUG_PAGE = json.dumps({"status":"ok","fake_flag":FLAG_FAKE})

sessions = {}
# قفل للسباق
upload_lock = threading.Lock()

class RaceHandler(http.server.BaseHTTPRequestHandler):
    def handle_one_request(self):
        try: super().handle_one_request()
        except (ConnectionResetError, BrokenPipeError): pass

    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path
        qs = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        sid = self._get_cookie('session')
        user = sessions.get(sid)

        if path == "/": self._serve_html(LOGIN_HTML)
        elif path == "/robots.txt": self._serve_text(ROBOTS_TXT)
        elif path == "/config": self._serve_json(CONFIG)
        elif path == "/debug": self._serve_json(DEBUG_PAGE)
        elif path == "/dashboard":
            if not user: self.send_error(403); return
            conn = sqlite3.connect(DB_PATH)
            files = conn.execute("SELECT stored_name, original_name FROM files WHERE uploader=?", (user['username'],)).fetchall()
            conn.close()
            file_links = "".join(f"<li><a href='/files/{f[0]}'>{f[1]}</a></li>" for f in files)
            self._serve_html(DASHBOARD.replace("%FILES%", file_links))
        elif path.startswith("/files/"):
            filename = path.split("/")[-1]
            filepath = os.path.join(UPLOAD_DIR, filename)
            if not os.path.exists(filepath):
                self.send_error(404); return
            # تنفيذ Python scripts
            if filename.endswith(".py"):
                import subprocess
                try:
                    output = subprocess.check_output([sys.executable, filepath], timeout=5, stderr=subprocess.STDOUT)
                    self._serve_text(output.decode())
                except Exception as e:
                    self._serve_text(str(e))
            else:
                self.send_response(200)
                self.send_header("Content-type", "application/octet-stream")
                self.end_headers()
                with open(filepath, 'rb') as f:
                    self.wfile.write(f.read())
        elif path == "/admin/flag":
            # CSRF: المسؤول يزور الرابط المُشارَك معه
            referer = self.headers.get('Referer','')
            if 'admin' in sid or 'admin' in referer:
                self._serve_text(f"Admin flag: {FLAG_FAKE}")
            else:
                self.send_error(403, "Admin only")
        elif path == "/logout":
            self.send_response(302)
            self.send_header("Set-Cookie","session=; expires=Thu, 01 Jan 1970 00:00:00 GMT")
            self.send_header("Location","/"); self.end_headers()
        else: self.send_error(404)

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length',0))
        body = self.rfile.read(content_length)
        path = urllib.parse.urlparse(self.path).path

        if path == "/login":
            data = urllib.parse.parse_qs(body.decode())
            user = data.get('username',[''])[0]; pwd = data.get('password',[''])[0]
            conn = sqlite3.connect(DB_PATH)
            row = conn.execute("SELECT id, username FROM users WHERE username=? AND password=?", (user,pwd)).fetchone()
            conn.close()
            if row:
                sid = uuid.uuid4().hex; sessions[sid] = {"username":row[1]}
                self.send_response(302)
                self.send_header("Set-Cookie", f"session={sid}; Path=/")
                self.send_header("Location", "/dashboard"); self.end_headers()
            else: self.send_error(403, "Invalid credentials")
        elif path == "/api/upload":
            # استخراج multipart (يدوي بسيط)
            ct = self.headers.get("Content-Type","")
            if "multipart/form-data" not in ct:
                self.send_error(400); return
            boundary = ct.split("boundary=")[1]
            parts = body.split(b'--'+boundary.encode())
            filename = None; filedata = None
            for part in parts:
                if b'Content-Disposition' in part:
                    if b'filename="' in part:
                        header, content = part.split(b'\r\n\r\n',1)
                        content = content.rstrip(b'\r\n--')
                        for line in header.split(b'\r\n'):
                            if b'filename="' in line:
                                fname = line.decode().split('filename="')[1].split('"')[0]
                                filename = fname
                                filedata = content
                                break
                        break
            if not filename or not filedata:
                self.send_error(400, "No file"); return
            # Race Condition: فحص الامتداد ثم حفظ
            if not is_image(filename):
                # لكن هل نمنع؟ لا، نسمح بالحفظ بعد 0.5 ثانية (سباق)
                time.sleep(0.5)
                # خلال هذا الوقت، يمكن استبدال الملف
                # لكن هنا لأغراض تعليمية: نخزن مباشرة
                ext = os.path.splitext(filename)[1]
                stored = uuid.uuid4().hex[:12] + ext
                filepath = os.path.join(UPLOAD_DIR, stored)
                with open(filepath, 'wb') as f:
                    f.write(filedata)
                conn = sqlite3.connect(DB_PATH)
                conn.execute("INSERT INTO files (original_name, stored_name, uploader) VALUES (?,?,?)",
                             (filename, stored, sessions.get(self._get_cookie('session'),{}).get('username','anon')))
                conn.commit(); conn.close()
                self._serve_text(f"File uploaded as {stored} (even if not image!)")
                return
            # إذا كان صورة، يحفظ فوراً
            ext = os.path.splitext(filename)[1]
            stored = uuid.uuid4().hex[:12] + ext
            filepath = os.path.join(UPLOAD_DIR, stored)
            with open(filepath, 'wb') as f:
                f.write(filedata)
            conn = sqlite3.connect(DB_PATH)
            conn.execute("INSERT INTO files (original_name, stored_name, uploader) VALUES (?,?,?)",
                         (filename, stored, sessions.get(self._get_cookie('session'),{}).get('username','anon')))
            conn.commit(); conn.close()
            self._serve_text(f"File uploaded as {stored}")
        elif path == "/share":
            sid = self._get_cookie('session'); user = sessions.get(sid)
            if not user: self.send_error(403); return
            # CSRF: المسؤول "يزور" الرابط المُشارَك
            file_url = urllib.parse.parse_qs(body.decode()).get('file_url',[''])[0]
            if file_url:
                # محاكاة زيارة المسؤول للرابط (نقوم بطلب GET داخلي)
                try:
                    import urllib.request
                    req = urllib.request.Request(file_url)
                    with urllib.request.urlopen(req, timeout=3) as resp:
                        content = resp.read().decode()
                    self._serve_text(f"Admin visited {file_url} and saw: {content[:200]}")
                except Exception as e:
                    self._serve_text(f"Admin could not visit {file_url}: {e}")
            else:
                self.send_error(400, "Missing file_url")
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
    server = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), RaceHandler)
    print(f"Web on {PORT}", flush=True)
    server.serve_forever()
