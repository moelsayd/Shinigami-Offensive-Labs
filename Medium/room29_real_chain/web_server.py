#!/usr/bin/env python3
import http.server, sys
from urllib.parse import parse_qs

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 6072

HTML_LOGIN = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Internal Portal</title>
    <style>
        body { background: #1a1a2e; color: #e0e0e0; font-family: 'Segoe UI', sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .login-box { background: #16213e; padding: 2rem; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }
        h2 { color: #e94560; }
        input { width: 100%; padding: 10px; margin: 8px 0; border: 1px solid #0f3460; background: #0f3460; color: #e0e0e0; border-radius: 5px; }
        input[type="submit"] { background: #e94560; border: none; font-weight: bold; cursor: pointer; }
        input[type="submit"]:hover { background: #c23152; }
    </style>
</head>
<body>
    <div class="login-box">
        <h2>Internal Portal</h2>
        <form method="POST" action="/login">
            <input type="text" name="username" placeholder="Username"><br>
            <input type="password" name="password" placeholder="Password"><br>
            <input type="submit" value="Log In">
        </form>
        <!-- Forgot to remove: SSH user: limited , pass: limited123 -->
    </div>
</body>
</html>"""

HTML_DASHBOARD = """<!DOCTYPE html>
<html>
<head>
    <title>Dashboard</title>
    <style>
        body { background: #1a1a2e; color: #e0e0e0; font-family: 'Segoe UI', sans-serif; padding: 2rem; }
        h2 { color: #e94560; }
        .info { background: #16213e; padding: 1rem; border-radius: 8px; }
    </style>
</head>
<body>
    <h2>Welcome, admin</h2>
    <div class="info">
        <p><strong>SSH Server:</strong> localhost:6073</p>
        <p><strong>User:</strong> limited</p>
        <p><strong>Password:</strong> limited123</p>
    </div>
</body>
</html>"""

class WebHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self._serve_html(HTML_LOGIN)
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path == "/login":
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode()
            data = parse_qs(body)
            user = data.get('username', [''])[0]
            pwd = data.get('password', [''])[0]
            if user == 'admin' and pwd == 'admin123':
                self._serve_html(HTML_DASHBOARD)
            else:
                self.send_error(403, "Invalid credentials")
        else:
            self.send_error(404)

    def _serve_html(self, html):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode())

    def log_message(self, format, *args):
        pass

if __name__ == "__main__":
    server = http.server.HTTPServer(("127.0.0.1", PORT), WebHandler)
    print(f"Web server running on http://127.0.0.1:{PORT}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
