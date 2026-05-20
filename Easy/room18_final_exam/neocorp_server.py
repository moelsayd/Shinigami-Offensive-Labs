#!/usr/bin/env python3
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8888
FLAG = "THM{basic_recon_chain_complete}"

INDEX_HTML = """<html><head><title>NeoCorp Portal</title></head><body>
<h1>Welcome to NeoCorp Internal Portal</h1>
<p>Nothing to see here... or maybe check the assets.</p>
</body></html>"""

LOGIN_PAGE = """<html><head><title>Secure Login</title></head><body>
<h2>Administrator Login</h2>
<form method="POST" action="/secure-login">
<input name="user" placeholder="Username"><br>
<input type="password" name="pass" placeholder="Password"><br>
<input type="submit" value="Log in">
</form>
</body></html>"""

MAIN_JS = """console.log("NeoCorp Portal initialised");
const DEBUG_MODE = true;
const DEV_ENDPOINT = "/internal/dev-notes.txt";
"""

DEV_NOTES = """Internal Developer Notes
================================
TODO:
- disable default creds
- admin:admin123 still active
- move login to /secure-login
"""

class NeoCorpHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/":
            self.serve_html(INDEX_HTML)
        elif path == "/login":
            self.serve_html("<h1>Login</h1><p>Under construction.</p>")
        elif path == "/assets/main.js":
            self.serve_js()
        elif path == "/internal/dev-notes.txt":
            self.serve_text(DEV_NOTES)
        elif path == "/secure-login":
            self.serve_html(LOGIN_PAGE)
        else:
            self.serve_404()

    def do_POST(self):
        if self.path == "/secure-login":
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode()
            params = parse_qs(body)
            user = params.get('user', [''])[0]
            pwd = params.get('pass', [''])[0]
            if user == "admin" and pwd == "admin123":
                self.send_response(200)
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                self.wfile.write(f"FLAG: {FLAG}\n".encode())
            else:
                self.send_response(403)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(b"<h3>Invalid credentials</h3><a href='/secure-login'>Try again</a>")
        else:
            self.send_404()

    def serve_html(self, html):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode())

    def serve_js(self):
        self.send_response(200)
        self.send_header("Content-type", "application/javascript")
        self.end_headers()
        self.wfile.write(MAIN_JS.encode())

    def serve_text(self, text):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(text.encode())

    def serve_404(self):
        self.send_response(404)
        self.end_headers()

    def log_message(self, format, *args):
        pass

if __name__ == "__main__":
    server = HTTPServer(("127.0.0.1", PORT), NeoCorpHandler)
    print(f"NeoCorp server running on http://127.0.0.1:{PORT}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
