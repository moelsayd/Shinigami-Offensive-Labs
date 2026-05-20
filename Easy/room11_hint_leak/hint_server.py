#!/usr/bin/env python3
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs

FLAG = "THM{ch41n3d_1nf0_l34k}"
DEV_NOTES = "TODO:\n- change admin password from admin123\n- update login page\n"
LOGIN_PAGE = """
<!DOCTYPE html>
<html>
<head><title>Admin Login</title></head>
<body>
  <h2>Restricted Login</h2>
  <form method="POST" action="/login">
    <input type="text" name="user" placeholder="Username"><br>
    <input type="password" name="pass" placeholder="Password"><br>
    <input type="submit" value="Log in">
  </form>
</body>
</html>
"""
INDEX_PAGE = "<h1>Welcome to the Company Portal</h1><p>Nothing to see here.</p>"

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(INDEX_PAGE.encode())
        elif self.path == "/dev-notes.txt":
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(DEV_NOTES.encode())
        elif self.path == "/login":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(LOGIN_PAGE.encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/login":
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
                self.wfile.write(b"<h3>Invalid credentials</h3><a href='/login'>Try again</a>")
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8888
    server = HTTPServer(("127.0.0.1", port), RequestHandler)
    print(f"Server running on http://127.0.0.1:{port}", file=sys.stderr)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
