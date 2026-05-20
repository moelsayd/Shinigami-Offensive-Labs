#!/usr/bin/env python3
import http.server, sys, os, json, urllib.parse

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8501
ROOM_DIR = os.path.dirname(os.path.abspath(__file__))
FAKE_ROOT = os.path.join(ROOM_DIR, "fake_root")
TRAP_DIR = os.path.join(ROOM_DIR, "trap")

INDEX_HTML = """<!DOCTYPE html>
<html><head><title>Document Server</title>
<style>body{background:#0a0c10;color:#c9d1d9;font-family:'Segoe UI',sans-serif;padding:2rem;}
h1{color:#f0883e;} a{color:#58a6ff;}</style></head><body>
<h1>Internal Document Server</h1>
<p>Download your documents <a href="/download?file=report.pdf">here</a>.</p>
</body></html>"""

ROBOTS_TXT = """User-agent: *
Disallow: /debug
Disallow: /trap
"""

DEBUG_INFO = json.dumps({"status":"ok","info":"Filesystem roots: /var/www/documents, /app/config","fake_flag":"THM{fake_debug_flag}"})

class TraversalHandler(http.server.BaseHTTPRequestHandler):
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
            self._serve_json(DEBUG_INFO)
        elif path == "/trap":
            self._serve_text(open(os.path.join(TRAP_DIR, "flag.txt")).read())
        elif path.startswith("/download"):
            file_param = qs.get('file', [None])[0]
            if not file_param:
                self.send_error(400, "Missing file parameter")
                return
            # بناء المسار مع وجود ثغرة Path Traversal
            requested_path = os.path.normpath(os.path.join(FAKE_ROOT, file_param))
            # لا نسمح بالخروج من ROOM_DIR (لكن هذا لا يمنع traversal داخل fake_root)
            if not requested_path.startswith(ROOM_DIR):
                self.send_error(403, "Access denied")
                return
            if os.path.isfile(requested_path):
                self.send_response(200)
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                with open(requested_path, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                self.send_error(404, "File not found")
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
    server = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), TraversalHandler)
    print(f"Web server on {PORT}", flush=True)
    server.serve_forever()
