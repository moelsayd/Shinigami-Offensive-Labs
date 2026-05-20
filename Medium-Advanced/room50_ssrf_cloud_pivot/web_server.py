#!/usr/bin/env python3
import http.server, sys, urllib.request, urllib.parse, urllib.error, os, json, re, sqlite3, uuid, time, threading

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8401
ROOM_DIR = os.path.dirname(os.path.abspath(__file__))
FLAG_FAKE = "THM{fake_web_flag}"

# ---------- HTML ----------
INDEX_HTML = """<!DOCTYPE html>
<html><head><title>CloudSync Portal</title>
<style>body{background:#0a0c10;color:#c9d1d9;font-family:'Segoe UI',sans-serif;padding:2rem;}
h1{color:#f0883e;} a{color:#58a6ff;}</style></head><body>
<h1>CloudSync Internal Portal</h1>
<p>Welcome to the internal document fetcher.</p>
<p><a href="/api/fetch?url=">Fetch external document</a></p>
<!-- Old legacy API: /api/fetch?url=... -->
</body></html>"""

ROBOTS_TXT = """User-agent: *
Disallow: /debug
Disallow: /admin
"""

DEBUG_PAGE = json.dumps({"status":"ok","info":"Internal IPs: 127.0.0.1","fake_flag":FLAG_FAKE})

class WebHandler(http.server.BaseHTTPRequestHandler):
    def handle_one_request(self):
        try:
            super().handle_one_request()
        except (ConnectionResetError, BrokenPipeError):
            pass

    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path
        qs = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)

        if path == "/":
            self._serve_html(INDEX_HTML)
        elif path == "/robots.txt":
            self._serve_text(ROBOTS_TXT)
        elif path == "/debug":
            self._serve_json(DEBUG_PAGE)
        elif path == "/api/fetch":
            url = qs.get('url', [None])[0]
            if not url:
                self._serve_text("Missing url parameter")
                return

            # ---- SSRF Filter (يحاول منع localhost) ----
            parsed = urllib.parse.urlparse(url)
            host = parsed.hostname or ""
            # منع الصريح
            blocked = ["localhost", "127.0.0.1", "::1", "0.0.0.0"]
            if host in blocked:
                self._serve_text("Blocked: direct localhost access")
                return

            # محاولة جلب الـ URL
            try:
                req = urllib.request.Request(url)
                with urllib.request.urlopen(req, timeout=4) as resp:
                    data = resp.read().decode()
                self._serve_text(data)
            except Exception as e:
                self._serve_text(f"Fetch error: {str(e)}")
        else:
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

    def _serve_json(self, data):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def log_message(self, format, *args):
        pass

if __name__ == "__main__":
    server = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), WebHandler)
    print(f"Web server on {PORT}", flush=True)
    server.serve_forever()
