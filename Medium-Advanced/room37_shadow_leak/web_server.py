#!/usr/bin/env python3
import http.server
import sys
import os
import json
import sqlite3
import zipfile
import io
import urllib.parse

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 7080
ROOM_DIR = os.path.dirname(os.path.abspath(__file__))
BACKUP_DIR = os.path.join(ROOM_DIR, "backup")
DB_PATH = os.path.join(ROOM_DIR, "shadow.db")
FLAG = "THM{graph_sh4d0w_l34k}"

# ======================= إعداد قاعدة البيانات =======================
conn = sqlite3.connect(DB_PATH)
conn.execute(
    "CREATE TABLE IF NOT EXISTS users "
    "(id INTEGER, username TEXT, password TEXT, role TEXT)"
)
conn.execute(
    "INSERT OR IGNORE INTO users VALUES (1, 'admin', 'admin123', 'admin')"
)
conn.execute(
    "INSERT OR IGNORE INTO users VALUES (2, 'dev', 'dev123', 'user')"
)
conn.execute(
    "CREATE TABLE IF NOT EXISTS secrets (id INTEGER, data TEXT)"
)
conn.execute("INSERT OR IGNORE INTO secrets VALUES (1, ?)", (FLAG,))
conn.commit()
conn.close()

# ======================= إعداد الأرشيف =======================
zip_buffer = io.BytesIO()
with zipfile.ZipFile(zip_buffer, 'w') as zf:
    zf.writestr(
        '.git/config',
        '[core]\n\trepositoryformatversion = 0\n\tfilemode = true\n'
        '[remote "origin"]\n\turl = http://internal/git/project.git'
    )
    zf.writestr(
        '.git/logs/HEAD',
        '0000000000000000000000000000000000000000 '
        '1111111111111111111111111111111111111111 '
        'dev <dev@neocorp.local> 1715347200 +0300\t'
        'commit: added debug endpoint\n'
        'Debug endpoint at /api/v1/debug/users'
    )
with open(os.path.join(BACKUP_DIR, "archive.zip"), "wb") as f:
    f.write(zip_buffer.getvalue())

# ======================= صفحات HTML =======================
INDEX_HTML = (
    '<!DOCTYPE html>'
    '<html lang="en"><head><meta charset="UTF-8"><title>NeoCorp Shadow</title>'
    '<style>body{background:#0a0c10;color:#c9d1d9;font-family:"Segoe UI",sans-serif;'
    'display:flex;justify-content:center;align-items:center;height:100vh;margin:0;}'
    'h1{color:#f0883e;}a{color:#58a6ff;}</style></head><body>'
    '<div><h1>NeoCorp Shadow Graph</h1><p>Internal data flow.</p></div>'
    '</body></html>'
)

ROBOTS_TXT = "User-agent: *\nDisallow: /backup/\nDisallow: /api/\n"

ADMIN_LOGIN = (
    '<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Admin Panel</title>'
    '<style>body{background:#0a0c10;display:flex;justify-content:center;'
    'align-items:center;height:100vh;font-family:"Segoe UI",sans-serif;}'
    '.box{background:#1a1c2b;padding:2rem;border-radius:12px;'
    'box-shadow:0 0 20px rgba(255,0,0,0.3);}h2{color:#e53170;}'
    'input{width:100%;padding:10px;margin:8px 0;background:#0d0f1a;'
    'border:1px solid #333;color:white;border-radius:5px;}'
    'input[type=submit]{background:#e53170;border:none;cursor:pointer;}'
    '</style></head><body><div class="box"><h2>Admin Login</h2>'
    '<form method="POST" action="/admin-panel">'
    '<input name="username" placeholder="Username"><br>'
    '<input type="password" name="password" placeholder="Password"><br>'
    '<input type="submit" value="Log In"></form></div></body></html>'
)

ADMIN_DASHBOARD = (
    '<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Dashboard</title>'
    '<style>body{background:#0a0c10;color:#c9d1d9;font-family:"Segoe UI",sans-serif;'
    'padding:2rem;}h2{color:#e53170;}.card{background:#1a1c2b;padding:1rem;'
    'border-radius:8px;}input,button{padding:8px;border-radius:5px;}'
    'input{background:#0d0f1a;border:1px solid #333;color:white;}'
    'button{background:#e53170;border:none;color:white;font-weight:bold;'
    'margin-left:5px;cursor:pointer;}.result{background:#0d0f1a;padding:1rem;'
    'margin-top:1rem;border-radius:5px;}</style></head><body>'
    '<h2>Admin Dashboard</h2><div class="card"><h3>User Lookup</h3>'
    '<form method="GET" action="/admin-panel/search">'
    '<input name="id" placeholder="User ID"><button>Search</button></form>'
    '<div class="result">%RESULT%</div></div>'
    '<a href="/logout" style="color:#e53170;">Logout</a></body></html>'
)


# ======================= معالج الطلبات المحصّن =======================
class ShadowHandler(http.server.BaseHTTPRequestHandler):
    # ---------- الحل الدائم لـ ConnectionResetError ----------
    def handle_one_request(self):
        try:
            super().handle_one_request()
        except (ConnectionResetError, BrokenPipeError):
            pass
    # ---------------------------------------------------------

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        qs = urllib.parse.parse_qs(parsed.query)

        if path == "/":
            self._serve_html(INDEX_HTML)
        elif path == "/robots.txt":
            self._serve_text(ROBOTS_TXT)
        elif path == "/backup/":
            self._serve_text("archive.zip\n")
        elif path == "/backup/archive.zip":
            self._serve_file(
                os.path.join(BACKUP_DIR, "archive.zip"), "application/zip"
            )
        elif path == "/api/v1/debug/users":
            conn = sqlite3.connect(DB_PATH)
            rows = conn.execute("SELECT username, password FROM users").fetchall()
            users = [{"username": r[0], "password": r[1]} for r in rows]
            self._serve_json(users)
            conn.close()
        elif path == "/admin-panel":
            if not self._is_auth():
                self._serve_html(ADMIN_LOGIN)
            else:
                self._serve_html(ADMIN_DASHBOARD.replace("%RESULT%", ""))
        elif path == "/admin-panel/search":
            if not self._is_auth():
                self.send_error(403)
                return
            uid = qs.get('id', [''])[0]
            if uid:
                conn = sqlite3.connect(DB_PATH)
                try:
                    cursor = conn.execute(
                        f"SELECT data FROM secrets WHERE id = {uid}"
                    )
                    row = cursor.fetchone()
                    result = f"Secret: {row[0]}" if row else "Not found"
                except Exception as e:
                    result = f"Error: {e}"
                finally:
                    conn.close()
            else:
                result = "Enter ID"
            self._serve_html(ADMIN_DASHBOARD.replace("%RESULT%", result))
        elif path == "/logout":
            self._clear_auth()
            self.send_response(302)
            self.send_header("Location", "/")
            self.end_headers()
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path == "/admin-panel":
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode()
            data = urllib.parse.parse_qs(body)
            username = data.get('username', [''])[0]
            password = data.get('password', [''])[0]
            conn = sqlite3.connect(DB_PATH)
            row = conn.execute(
                "SELECT * FROM users WHERE username=? AND password=?",
                (username, password)
            ).fetchone()
            conn.close()
            if row:
                self.send_response(302)
                self.send_header("Set-Cookie", "session=admin; Path=/")
                self.send_header("Location", "/admin-panel")
                self.end_headers()
            else:
                self.send_error(403, "Invalid credentials")
        else:
            self.send_error(404)

    # ========== دوال مساعدة ==========
    def _is_auth(self):
        return 'session=admin' in self.headers.get('Cookie', '')

    def _clear_auth(self):
        self.send_header(
            "Set-Cookie",
            "session=; expires=Thu, 01 Jan 1970 00:00:00 GMT"
        )

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

    def _serve_file(self, filepath, content_type):
        if not os.path.exists(filepath):
            self.send_error(404)
            return
        self.send_response(200)
        self.send_header("Content-type", content_type)
        self.end_headers()
        with open(filepath, 'rb') as f:
            self.wfile.write(f.read())

    def log_message(self, format, *args):
        pass  # صامت تماماً


# ======================= بدء الخادم =======================
if __name__ == "__main__":
    server = http.server.ThreadingHTTPServer(
        ("127.0.0.1", PORT), ShadowHandler
    )
    print("Server active", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
