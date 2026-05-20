#!/usr/bin/env python3
import sys, os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 4040
ROOM_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(ROOM_DIR, "templates")

class LFIHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/view":
            params = parse_qs(parsed.query)
            page = params.get("page", ["home"])[0]

            # Prevent absolute paths and dangerous traversal
            if page.startswith("/") or ".." not in page:
                # For a realistic LFI, we allow ".." but restrict to room dir
                pass
            
            # Resolve path relative to templates folder, then normalize
            requested_path = os.path.normpath(os.path.join(TEMPLATES_DIR, page))
            # Ensure it stays inside ROOM_DIR for security
            if not requested_path.startswith(ROOM_DIR):
                self.send_error(403, "Access denied")
                return
            
            if os.path.isfile(requested_path):
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                with open(requested_path, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self.send_error(404, "File not found")
        else:
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            html = """<html><body>
            <h1>Welcome to the Website</h1>
            <p>Use the /view endpoint to see pages: <a href="/view?page=home">home</a> | <a href="/view?page=about">about</a></p>
            </body></html>"""
            self.wfile.write(html.encode())

    def log_message(self, format, *args):
        pass

if __name__ == "__main__":
    server = HTTPServer(("127.0.0.1", PORT), LFIHandler)
    print(f"Server running on http://127.0.0.1:{PORT}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
