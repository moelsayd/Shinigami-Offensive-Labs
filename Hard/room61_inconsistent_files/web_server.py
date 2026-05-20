#!/usr/bin/env python3
import http.server, sys, os, json, urllib.parse

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 9601
ROOM_DIR = os.path.dirname(os.path.abspath(__file__))
FLAG_FAKE = "THM{fake_web_inconsistent}"
API_KEY = "oracle_api_key_456"

INDEX_HTML = """<!DOCTYPE html>
<html><head><title>FileCorp</title>
<style>body{background:#0a0c10;color:#c9d1d9;font-family:'Segoe UI',sans-serif;padding:2rem;}
h1{color:#f0883e;}</style></head><body>
<h1>FileCorp Document Server</h1>
<p>Access internal documents <a href="/download?file=report.txt">here</a>.</p>
</body></html>"""

ROBOTS_TXT = """User-agent: *
Disallow: /config/
Disallow: /debug
Disallow: /api
"""

CONFIG = json.dumps({
    "api_key": API_KEY,
    "oracle_service": "http://localhost:9602/decrypt",
    "note": "Oracle expects base64 IV+ciphertext"
})

DEBUG_PAGE = json.dumps({"status":"ok","fake_flag":FLAG_FAKE})

class WebHandler(http.server.BaseHTTPRequestHandler):
    def handle_one_request(self):
        try: super().handle_one_request()
        except (ConnectionResetError, BrokenPipeError): pass

    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path
        qs = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)

        if path == "/": self._serve_html(INDEX_HTML)
        elif path == "/robots.txt": self._serve_text(ROBOTS_TXT)
        elif path == "/config": self._serve_json(CONFIG)
        elif path == "/debug": self._serve_json(DEBUG_PAGE)
        elif path == "/download":
            filename = qs.get('file', [None])[0]
            if filename == "flag.txt.enc":
                self.send_error(403, "Direct download of encrypted flag is blocked")
                return
            elif filename == "report.txt":
                self._serve_text("This is a sample report. Nothing interesting.")
            else:
                self.send_error(404, "File not found")
        elif path.startswith("/api/file"):
            # Inconsistent access: API path يسمح بقراءة flag.txt.enc
            filename = qs.get('file', [None])[0]
            if filename == "flag.txt.enc":
                enc_path = os.path.join(ROOM_DIR, "flag.txt.enc")
                if os.path.exists(enc_path):
                    with open(enc_path, 'rb') as f:
                        data = f.read()
                    self.send_response(200)
                    self.send_header("Content-type", "application/octet-stream")
                    self.end_headers()
                    self.wfile.write(data)
                else:
                    self.send_error(404)
            else:
                self.send_error(404, "Unknown file")
        else:
            self.send_error(404)

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
