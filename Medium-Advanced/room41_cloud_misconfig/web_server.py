#!/usr/bin/env python3
import http.server, sys, os, json, urllib.parse

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 7084
ROOM_DIR = os.path.dirname(os.path.abspath(__file__))
FAKE_FLAG = "THM{fake_env_flag}"

INDEX_HTML = """<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><title>Cloud Corp</title>
<style>body{background:#0a0c10;color:#c9d1d9;font-family:'Segoe UI',sans-serif;display:flex;justify-content:center;align-items:center;height:100vh;margin:0;}
h1{color:#f0883e;}</style></head><body><h1>Cloud Corp Portal</h1></body></html>"""

ENV_CONTENT = f"""DB_HOST=localhost
DB_USER=root
DB_PASS=root123
AWS_ACCESS_KEY_ID=AKIA1234567890ABCDEF
AWS_SECRET_ACCESS_KEY=abcdef1234567890abcdef1234567890abcdef12
S3_ENDPOINT=http://localhost:7085
BUCKET_NAME=internal-data
FLAG={FAKE_FLAG}
"""

ROBOTS_TXT = """User-agent: *
Disallow: /.env
Disallow: /admin/
Disallow: /storage/
"""

class WebHandler(http.server.BaseHTTPRequestHandler):
    def handle_one_request(self):
        try:
            super().handle_one_request()
        except (ConnectionResetError, BrokenPipeError):
            pass

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/":
            self._serve_html(INDEX_HTML)
        elif path == "/robots.txt":
            self._serve_text(ROBOTS_TXT)
        elif path == "/.env":
            self._serve_text(ENV_CONTENT)
        elif path == "/admin/":
            self._serve_text("Admin area under construction")
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

    def log_message(self, format, *args):
        pass

if __name__ == "__main__":
    server = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), WebHandler)
    print("Server active", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
