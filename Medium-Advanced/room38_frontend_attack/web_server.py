#!/usr/bin/env python3
import http.server, sys, os, json, sqlite3, urllib.parse

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 7081
ROOM_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(ROOM_DIR, "users.db")
FLAG = "THM{fr0nt3nd_s3cr3ts}"
FAKE_FLAG = "THM{fake_frontend_flag}"

# ======================= صفحات HTML / JS =======================
INDEX_HTML = """<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><title>React App</title>
<style>body{background:#0a0c10;color:#c9d1d9;font-family:'Segoe UI',sans-serif;display:flex;justify-content:center;align-items:center;height:100vh;margin:0;}
h1{color:#f0883e;}</style></head>
<body><div id="root"><h1>React App</h1><p>Loading...</p></div>
<script src="/static/app.js"></script></body></html>"""

APP_JS = """// React 17.0.2 – production build
(function() {
  // Hidden config exposed on window by mistake
  window.__CONFIG__ = {
    admin: "/super/secret/panel",
    debug: "/api/v1/debug",
    version: "1.0.0"
  };
  // DEV_CREDS admin:React2024!
  console.log("App mounted");
})();"""

ROBOTS_TXT = """User-agent: *
Disallow: /admin/
Disallow: /api/
Disallow: /fake-secret
"""

LOGIN_PAGE = """<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Super Admin</title>
<style>body{background:#0a0c10;display:flex;justify-content:center;align-items:center;height:100vh;font-family:'Segoe UI',sans-serif;}
.box{background:#1a1c2b;padding:2rem;border-radius:12px;box-shadow:0 0 25px rgba(0,255,0,0.3);}
h2{color:#00ff00;} input{width:100%;padding:10px;margin:8px 0;background:#0d0f1a;border:1px solid #333;color:white;border-radius:5px;}
input[type=submit]{background:#00aa00;border:none;cursor:pointer;font-weight:bold;}
</style></head><body><div class="box"><h2>Super Secret Panel</h2>
<form method="POST" action="/super/secret/panel">
<input name="username" placeholder="Username"><br>
<input type="password" name="password" placeholder="Password"><br>
<input type="submit" value="Log In"></form></div></body></html>"""

ADMIN_DASHBOARD = """<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Admin Dashboard</title>
<style>body{background:#0a0c10;color:#c9d1d9;font-family:'Segoe UI',sans-serif;padding:2rem;}
h2{color:#00ff00;} .card{background:#1a1c2b;padding:1rem;border-radius:8px;margin:1rem 0;}
input,button{padding:8px;border-radius:5px;} input{background:#0d0f1a;border:1px solid #333;color:white;}
button{background:#00aa00;border:none;color:white;font-weight:bold;margin-left:5px;cursor:pointer;}
.result{background:#0d0f1a;padding:1rem;margin-top:1rem;border-radius:5px;}</style></head><body>
<h2>Admin Dashboard</h2>
<div class="card"><h3>User Search</h3>
<form method="GET" action="/super/secret/panel/search"><input name="id" placeholder="User ID"><button>Search</button></form>
<div class="result">%RESULT%</div></div><a href="/logout" style="color:#00ff00;">Logout</a></body></html>"""

class FrontendHandler(http.server.BaseHTTPRequestHandler):
    def handle_one_request(self):
        try:
            super().handle_one_request()
        except (ConnectionResetError, BrokenPipeError):
            pass

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        qs = urllib.parse.parse_qs(parsed.query)

        if path == "/":
            self._serve_html(INDEX_HTML)
        elif path == "/robots.txt":
            self._serve_text(ROBOTS_TXT)
        elif path == "/static/app.js":
            self._serve_text(APP_JS, "application/javascript")
        elif path == "/super/secret/panel":
            if not self._is_auth():
                self._serve_html(LOGIN_PAGE)
            else:
                self._serve_html(ADMIN_DASHBOARD.replace("%RESULT%", ""))
        elif path == "/super/secret/panel/search":
            if not self._is_auth():
                self.send_error(403); return
            uid = qs.get('id', [''])[0]
            if uid:
                conn = sqlite3.connect(DB_PATH)
                try:
                    cursor = conn.execute(f"SELECT data FROM secrets WHERE id = {uid}")
                    row = cursor.fetchone()
                    result = f"Secret: {row[0]}" if row else "Not found"
                except Exception as e:
                    result = f"Error: {e}"
                finally:
                    conn.close()
            else:
                result = "Enter ID"
            self._serve_html(ADMIN_DASHBOARD.replace("%RESULT%", result))
        elif path == "/api/v1/debug":
            self._serve_json({"status":"ok","note":"No sensitive data here"})
        elif path == "/fake-secret":
            self._serve_text(f"FLAG={FAKE_FLAG}")
        elif path == "/logout":
            self.send_response(302)
            self.send_header("Set-Cookie", "session=; expires=Thu, 01 Jan 1970 00:00:00 GMT")
            self.send_header("Location", "/")
            self.end_headers()
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path == "/super/secret/panel":
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode()
            data = urllib.parse.parse_qs(body)
            user = data.get('username', [''])[0]
            pwd = data.get('password', [''])[0]
            # Credentials from JS comment: admin:React2024!
            if user == 'admin' and pwd == 'React2024!':
                self.send_response(302)
                self.send_header("Set-Cookie", "session=admin; Path=/")
                self.send_header("Location", "/super/secret/panel")
                self.end_headers()
            else:
                self.send_error(403, "Invalid credentials")
        else:
            self.send_error(404)

    def _is_auth(self):
        return 'session=admin' in self.headers.get('Cookie', '')

    def _serve_html(self, html):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode())

    def _serve_text(self, text, ctype="text/plain"):
        self.send_response(200)
        self.send_header("Content-type", ctype)
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
    server = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), FrontendHandler)
    print("Server active", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
