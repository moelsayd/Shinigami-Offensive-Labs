#!/usr/bin/env python3
import http.server, sys, os

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 6084
ROOM_DIR = os.path.dirname(os.path.abspath(__file__))
DOCUMENTS_DIR = os.path.join(ROOM_DIR, "documents")
FAKE_ROOT = os.path.join(ROOM_DIR, "fake_root")
FLAG = "THM{path_tr4v3rs4l_l34k}"

INDEX_HTML = """<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><title>Secure File Server</title>
<style>
    body { background: #0a0c10; color: #c9d1d9; font-family: 'Segoe UI', sans-serif; padding: 2rem; }
    h1 { color: #f0883e; }
    a { color: #58a6ff; }
    .note { color: #8b949e; font-size: 0.9rem; }
    /* <!-- Admin note: debug info at /debug --> */
</style>
</head>
<body>
    <h1>Internal File Server</h1>
    <p>Welcome to the document download portal.</p>
    <ul>
        <li><a href="/download?file=report.pdf">Download Report</a></li>
    </ul>
    <p class="note">For administration, check <a href="/robots.txt">robots.txt</a></p>
</body>
</html>"""

ROBOTS_TXT = """User-agent: *
Disallow: /backup/
Disallow: /debug
"""

BACKUP_CREDS = """# Internal Credentials Backup
# WARNING: This is a decoy file. The real flag is located in /root/flag.txt
admin:admin123
user:password123
"""

class TraversalHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self._serve_html(INDEX_HTML)
        elif self.path == "/robots.txt":
            self._serve_text(ROBOTS_TXT)
        elif self.path == "/debug":
            info = f"""Server: Python/3.x
Document Root: {DOCUMENTS_DIR}
Allowed Endpoints: /download?file=...
System Info: Linux localhost 5.15.0-generic
"""
            self._serve_text(info)
        elif self.path.startswith("/download"):
            from urllib.parse import urlparse, parse_qs
            qs = parse_qs(urlparse(self.path).query)
            file_param = qs.get('file', [None])[0]
            if not file_param:
                self.send_error(400, "Missing file parameter")
                return
            # Intentionally vulnerable: no path sanitization
            full_path = os.path.normpath(os.path.join(DOCUMENTS_DIR, file_param))
            # Ensure we don't escape ROOM_DIR for safety, but allow traversal within FAKE_ROOT
            if not full_path.startswith(ROOM_DIR):
                self.send_error(403, "Access denied (outside room)")
                return
            if os.path.isfile(full_path):
                self.send_response(200)
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                with open(full_path, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                self.send_error(404, "File not found")
        elif self.path == "/backup/creds.txt":
            self._serve_text(BACKUP_CREDS)
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
    server = http.server.HTTPServer(("127.0.0.1", PORT), TraversalHandler)
    print(f"Path traversal server running on http://127.0.0.1:{PORT}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
