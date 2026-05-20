#!/usr/bin/env python3
import http.server, sys, os, json, sqlite3, urllib.parse, time

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 7401
ROOM_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(ROOM_DIR, "dev.db")
FLAG_REAL = "THM{d3v_endp01nt_l34k}"
FLAG_FAKE = "THM{fake_debug_env}"
DEV_TOKEN = "devtoken123"

INDEX_HTML = """<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><title>NeoCorp Operations</title>
<style>body{background:#0a0c10;color:#c9d1d9;font-family:'Segoe UI',sans-serif;display:flex;justify-content:center;align-items:center;height:100vh;margin:0;}
h1{color:#f0883e;}</style></head><body><h1>Operations Dashboard</h1></body></html>"""

ROBOTS_TXT = """User-agent: *
Disallow: /debug/
Disallow: /internal/
Disallow: /admin/
"""

DEBUG_ENV = json.dumps({
    "DB_HOST": "localhost",
    "DB_USER": "root",
    "DB_PASS": "fake123",
    "FLAG": FLAG_FAKE,
    "NOTE": "This is a decoy environment"
})

METRICS_PAGE = json.dumps({
    "cpu": "12%",
    "memory": "34%",
    "internal_service": "http://localhost:7555",
    "access_token": DEV_TOKEN,
    "note": "Devtools at /admin/devtools require header X-Dev-Token"
})

DEVTOOLS_LOGIN = """<!DOCTYPE html>
<html><head><title>DevTools</title>
<style>body{background:#0a0c10;color:#c9d1d9;font-family:'Segoe UI',sans-serif;padding:2rem;}
h2{color:#00ff00;} .card{background:#1a1c2b;padding:1rem;border-radius:8px;margin:1rem 0;}
input,button{padding:8px;border-radius:5px;} input{background:#0d0f1a;border:1px solid #333;color:white;}
button{background:#00aa00;border:none;color:white;font-weight:bold;margin-left:5px;cursor:pointer;}
.result{background:#0d0f1a;padding:1rem;margin-top:1rem;border-radius:5px;}</style></head><body>
<h2>Developer Tools</h2>
<div class="card"><h3>User Search</h3>
<form method="GET" action="/admin/devtools"><input name="id" placeholder="User ID"><button>Search</button></form>
<div class="result">%RESULT%</div></div></body></html>"""

class DevHandler(http.server.BaseHTTPRequestHandler):
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
        elif path == "/debug/env":
            self._serve_json(DEBUG_ENV)
        elif path == "/internal/metrics":
            self._serve_json(METRICS_PAGE)
        elif path == "/admin/devtools":
            token = self.headers.get("X-Dev-Token", "")
            if token != DEV_TOKEN:
                self.send_response(403)
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                self.wfile.write(b"Missing or invalid X-Dev-Token header")
                return
            uid = qs.get('id', [None])[0]
            if uid:
                conn = sqlite3.connect(DB_PATH)
                try:
                    # SQLi vulnerable
                    query = f"SELECT name, role FROM users WHERE id = {uid}"
                    row = conn.execute(query).fetchone()
                    if row:
                        result = f"User: {row[0]}, Role: {row[1]}"
                    else:
                        result = "Not found"
                except Exception as e:
                    result = f"Error: {e}"
                finally:
                    conn.close()
            else:
                result = "Enter ID"
            html = DEVTOOLS_LOGIN.replace("%RESULT%", result)
            self._serve_html(html)
        else:
            self.send_error(404)

    def do_POST(self):
        self.send_error(404)

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

    def _serve_json(self, obj):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(obj).encode())

    def log_message(self, format, *args):
        pass

if __name__ == "__main__":
    server = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), DevHandler)
    print("Server active", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
