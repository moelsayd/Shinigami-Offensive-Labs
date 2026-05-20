#!/usr/bin/env python3
import http.server, sys, urllib.request, urllib.parse, os
from urllib.parse import parse_qs

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 6082
INTERNAL_HOST = "127.0.0.1"
INTERNAL_PORT = 6083
FAKE_FLAG = "THM{fake_admin_flag}"

LOGIN_HTML = """<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><title>Corporate Portal</title>
<style>
    body{background:#0d1117;color:#c9d1d9;font-family:'Segoe UI',sans-serif;display:flex;justify-content:center;align-items:center;height:100vh;margin:0;}
    .box{background:#161b22;padding:2rem;border-radius:12px;box-shadow:0 0 25px rgba(255,0,0,0.2);}
    h2{color:#58a6ff;} input{width:100%;padding:10px;margin:8px 0;border:1px solid #30363d;background:#0d1117;color:#c9d1d9;border-radius:6px;}
    input[type="submit"]{background:#238636;border:none;font-weight:bold;cursor:pointer;}
    input[type="submit"]:hover{background:#2ea043;}
</style></head>
<body><div class="box"><h2>Login</h2>
<form method="POST" action="/login">
<input name="username" placeholder="Username"><br>
<input type="password" name="password" placeholder="Password"><br>
<input type="submit" value="Sign In">
</form>
<!-- DevNote: temp login admin / password123 -->
</div></body></html>"""

DASHBOARD = """<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><title>Dashboard</title>
<style>
    body{background:#0d1117;color:#c9d1d9;font-family:'Segoe UI',sans-serif;padding:2rem;}
    h2{color:#58a6ff;} .card{background:#161b22;padding:1rem;border-radius:8px;margin:1rem 0;}
    input,button{padding:10px;border-radius:6px;}
    input{background:#0d1117;border:1px solid #30363d;color:#c9d1d9;width:60%;}
    button{background:#238636;border:none;font-weight:bold;color:white;margin-left:10px;cursor:pointer;}
    .result{background:#0d1117;padding:1rem;margin-top:1rem;border-radius:6px;border:1px solid #30363d;white-space:pre-wrap;}
</style></head>
<body>
<h2>Dashboard</h2>
<div class="card">
    <h3>Internal URL Fetcher</h3>
    <form method="GET" action="/fetch">
        <input name="url" placeholder="http://127.0.0.1:6083/admin" value="">
        <button>Fetch</button>
    </form>
    <div class="result">%RESULT%</div>
</div>
<a href="/logout" style="color:#58a6ff;">Logout</a>
</body></html>"""

BACKUP_CODE = """# Backup of fetch handler – internal
# TODO: improve filter to block hex/decimal IPs
def fetch_url(url):
    if not url.startswith("http://127.0.0.1/"):
        return "Error: only internal URLs allowed"
    if "admin" in url.lower():
        return "Error: restricted path"
    # ... fetch logic ...
    return urllib.request.urlopen(url).read()
"""

class WebHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self._serve_html(LOGIN_HTML)
        elif self.path == "/robots.txt":
            self._serve_text("User-agent: *\nDisallow: /backup/\nDisallow: /fake-admin\n")
        elif self.path == "/fake-admin":
            self._serve_text(f"Fake Admin Panel\nFlag: {FAKE_FLAG}")
        elif self.path == "/backup/config.bak":
            self._serve_text(BACKUP_CODE)
        elif self.path.startswith("/fetch"):
            if not self._is_auth():
                self.send_error(403); return
            qs = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            url = qs.get('url', [None])[0]
            if not url:
                self._serve_html(DASHBOARD.replace("%RESULT%", "No URL provided"))
                return

            # ------------------ SSRF Filter ------------------
            if not url.startswith("http://127.0.0.1/"):
                self._serve_html(DASHBOARD.replace("%RESULT%", "Error: only internal URLs allowed (http://127.0.0.1/...)"))
                return
            if "admin" in url.lower():
                self._serve_html(DASHBOARD.replace("%RESULT%", "Error: restricted path (contains 'admin')"))
                return
            # --------------------------------------------------
            try:
                req = urllib.request.Request(url)
                with urllib.request.urlopen(req, timeout=5) as response:
                    data = response.read().decode()
                self._serve_html(DASHBOARD.replace("%RESULT%", data))
            except Exception as e:
                self._serve_html(DASHBOARD.replace("%RESULT%", f"Error: {str(e)}"))
        elif self.path == "/logout":
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
            data = parse_qs(body)
            user = data.get('username', [''])[0]
            pwd = data.get('password', [''])[0]
            if user == 'admin' and pwd == 'password123':
                self.send_response(302)
                self.send_header("Set-Cookie", "session=admin; Path=/")
                self.send_header("Location", "/fetch")
                self.end_headers()
            else:
                self.send_error(403, "Bad credentials")
        else:
            self.send_error(404)

    def _is_auth(self):
        return 'session=admin' in self.headers.get('Cookie', '')

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

    def log_message(self, format, *args): pass

if __name__ == "__main__":
    server = http.server.HTTPServer(("127.0.0.1", PORT), WebHandler)
    print(f"Web server running on http://127.0.0.1:{PORT}", flush=True)
    server.serve_forever()
server.server_close()
