#!/usr/bin/env python3
import sys, json, hmac, hashlib, base64, time, http.server
from urllib.parse import parse_qs

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 6070
SECRET = b"secret123"
FLAG = "THM{p4ssw0rd_r3us3_p1vot}"

def b64url_encode(data):
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode()

def b64url_decode(data):
    padding = 4 - len(data) % 4
    if padding != 4:
        data += "=" * padding
    return base64.urlsafe_b64decode(data)

def jwt_create(payload):
    header = {"alg": "HS256", "typ": "JWT"}
    h = b64url_encode(json.dumps(header, separators=(",", ":")).encode())
    p = b64url_encode(json.dumps(payload, separators=(",", ":")).encode())
    sig = hmac.new(SECRET, f"{h}.{p}".encode(), hashlib.sha256).digest()
    s = b64url_encode(sig)
    return f"{h}.{p}.{s}"

def jwt_verify(token):
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        h, p, s = parts
        expected = b64url_encode(hmac.new(SECRET, f"{h}.{p}".encode(), hashlib.sha256).digest())
        if s != expected:
            return None
        return json.loads(b64url_decode(p))
    except:
        return None

class JWTHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self._serve_html("<h1>Login</h1><form method='POST' action='/login'>User: <input name='user'><br>Pass: <input name='pass' type='password'><br><input type='submit'></form>")
        elif self.path == "/notes":
            token = self.headers.get("Authorization", "").replace("Bearer ", "")
            payload = jwt_verify(token)
            if not payload:
                self.send_error(401, "Invalid token")
                return
            if payload.get("role") == "admin":
                self.send_response(200)
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                self.wfile.write(f"Admin notes: The FTP service at port 6071 uses the same password as the web admin.\nAlso, here is your flag: {FLAG}\n".encode())
            else:
                self._serve_html("<h2>Internal Notes</h2><p>FTP service at <code>localhost:6071</code> – same admin password.</p>")
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path == "/login":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode()
            data = parse_qs(body)
            user = data.get("user", [""])[0]
            pwd = data.get("pass", [""])[0]
            if user == "admin" and pwd == "admin123":
                payload = {"user": "admin", "role": "user", "iat": int(time.time())}
                token = jwt_create(payload)
                self._respond_json({"token": token})
            else:
                self.send_error(403, "Invalid credentials")
        else:
            self.send_error(404)

    def _serve_html(self, html):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode())

    def _respond_json(self, data):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def log_message(self, format, *args):
        pass

if __name__ == "__main__":
    server = http.server.HTTPServer(("127.0.0.1", PORT), JWTHandler)
    print(f"Web server running on http://127.0.0.1:{PORT}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
