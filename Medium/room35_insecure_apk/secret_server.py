import http.server, sys, socketserver
from urllib.parse import parse_qs

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 9999
REAL_FLAG = "THM{apk_revers3_eng}"
FAKE_FLAG = "THM{fake_apk_flag}"

LOGIN_PAGE = """<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Secret Admin</title>
<style>body{background:#0a0c10;color:#c9d1d9;font-family:'Segoe UI',sans-serif;display:flex;justify-content:center;align-items:center;height:100vh;margin:0;}
.box{background:#1a1c2b;padding:2rem;border-radius:12px;box-shadow:0 0 20px rgba(0,255,0,0.2);}
input{width:100%;padding:10px;margin:8px 0;border:1px solid #333;background:#0d0f1a;color:white;border-radius:5px;}
input[type=submit]{background:#00aa00;border:none;cursor:pointer;font-weight:bold;}
input[type=submit]:hover{background:#008800;}
</style></head><body><div class="box"><h2>Secret Admin</h2>
<form method="POST" action="/login">
<input name="username" placeholder="Username"><br>
<input type="password" name="password" placeholder="Password"><br>
<input type="submit" value="Login">
</form></div></body></html>"""

class RobustHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self._serve_html(LOGIN_PAGE)
        elif self.path == "/robots.txt":
            self._serve_text("User-agent: *\nDisallow: /backup")
        elif self.path == "/backup":
            self._serve_text(FAKE_FLAG)
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path == "/login":
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode()
            data = parse_qs(body)
            user = data.get('username', [''])[0]
            pwd = data.get('password', [''])[0]
            if user == 'admin' and pwd == 'supersecret':
                self.send_response(200)
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                self.wfile.write(f"Welcome admin! Flag: {REAL_FLAG}\n".encode())
            else:
                self.send_error(403, "Invalid credentials")
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

# صف خادم مخصص يتجاهل أخطاء الاتصال بدون طباعة
class QuietServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

    def handle_error(self, request, client_address):
        pass  # نتجاهل الاستثناءات بهدوء

if __name__ == "__main__":
    server = QuietServer(("127.0.0.1", PORT), RobustHandler)
    print(f"Secret server on http://127.0.0.1:{PORT}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
