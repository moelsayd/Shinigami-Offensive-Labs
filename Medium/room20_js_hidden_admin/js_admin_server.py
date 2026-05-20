#!/usr/bin/env python3
import sys, os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 7071
ROOM_DIR = os.path.dirname(os.path.abspath(__file__))
TARGET_DIR = os.path.join(ROOM_DIR, "target")
FLAG = "THM{js_h1dd3n_p4n3l}"

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        # Serve static files from target directory
        file_path = os.path.normpath(os.path.join(TARGET_DIR, path.lstrip('/')))
        if os.path.isfile(file_path) and file_path.startswith(TARGET_DIR):
            self.send_response(200)
            # Set correct MIME type based on extension
            ext = os.path.splitext(file_path)[1]
            if ext == '.html':
                self.send_header("Content-type", "text/html")
            elif ext == '.js':
                self.send_header("Content-type", "application/javascript")
            else:
                self.send_header("Content-type", "text/plain")
            self.end_headers()
            with open(file_path, "rb") as f:
                self.wfile.write(f.read())
            return

        # Redirect root to index.html
        if path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            with open(os.path.join(TARGET_DIR, "index.html"), "rb") as f:
                self.wfile.write(f.read())
            return

        # 404
        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/x7/admin-panel/login":
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode()
            params = parse_qs(body)
            user = params.get('user', [''])[0]
            pwd = params.get('pass', [''])[0]
            if user == "admin" and pwd == "admin123":
                self.send_response(200)
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                self.wfile.write(f"Login successful! Flag: {FLAG}\n".encode())
            else:
                self.send_response(403)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(b"<h3>Invalid credentials</h3><a href='/x7/admin-panel'>Try again</a>")
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass

if __name__ == "__main__":
    server = HTTPServer(("127.0.0.1", PORT), Handler)
    print(f"Server running on http://127.0.0.1:{PORT}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
