#!/usr/bin/env python3
import http.server, sys, json, os, urllib.parse

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8901
ROOM_DIR = os.path.dirname(os.path.abspath(__file__))
FLAG_FAKE = "THM{fake_web_portal}"

INDEX_HTML = """<!DOCTYPE html>
<html><head><title>NeoCorp Cloud Portal</title>
<style>body{background:#0a0c10;color:#c9d1d9;font-family:'Segoe UI',sans-serif;display:flex;justify-content:center;align-items:center;height:100vh;margin:0;}
h1{color:#f0883e;}</style></head><body><h1>Welcome to NeoCorp Cloud Portal</h1>
<script src="/assets/app.bundle.js"></script></body></html>"""

APP_JS = """// NeoCorp Cloud v2.1.4
window.CONFIG = {
  API_BASE: "/api/v2/",
  ADMIN_PANEL: "/internal/console",
  DEBUG: true,
  NOTE: "API requires custom header X-API-Key: neo_internal_key"
};
console.log("App initialized");"""

ROBOTS_TXT = """User-agent: *
Disallow: /assets/
Disallow: /api/
"""

DEBUG_PAGE = json.dumps({"status":"ok","fake_flag":FLAG_FAKE})

class WebHandler(http.server.BaseHTTPRequestHandler):
    def handle_one_request(self):
        try: super().handle_one_request()
        except: pass

    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path
        if path == "/": self._serve_html(INDEX_HTML)
        elif path == "/assets/app.bundle.js": self._serve_text(APP_JS, "application/javascript")
        elif path == "/robots.txt": self._serve_text(ROBOTS_TXT)
        elif path == "/debug": self._serve_json(DEBUG_PAGE)
        else: self.send_error(404)

    def _serve_html(self, html):
        self.send_response(200); self.send_header("Content-type","text/html"); self.end_headers(); self.wfile.write(html.encode())
    def _serve_text(self, text, ctype="text/plain"):
        self.send_response(200); self.send_header("Content-type",ctype); self.end_headers(); self.wfile.write(text.encode())
    def _serve_json(self, data):
        self.send_response(200); self.send_header("Content-type","application/json"); self.end_headers(); self.wfile.write(json.dumps(data).encode())
    def log_message(self, format, *args): pass

if __name__ == "__main__":
    server = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), WebHandler)
    print(f"Web on {PORT}", flush=True)
    server.serve_forever()
