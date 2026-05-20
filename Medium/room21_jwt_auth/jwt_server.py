#!/usr/bin/env python3
import sys, json, hmac, hashlib, base64, time, http.server
from urllib.parse import parse_qs

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 6062
SECRET = b"admin"
FLAG = "THM{jwt_w34k_s3cr3t}"

def base64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode()

def base64url_decode(data: str) -> bytes:
    padding = 4 - len(data) % 4
    if padding != 4:
        data += "=" * padding
    return base64.urlsafe_b64decode(data)

def jwt_create(payload: dict) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    header_b64 = base64url_encode(json.dumps(header, separators=(",", ":")).encode())
    payload_b64 = base64url_encode(json.dumps(payload, separators=(",", ":")).encode())
    signing_input = f"{header_b64}.{payload_b64}".encode()
    signature = hmac.new(SECRET, signing_input, hashlib.sha256).digest()
    sig_b64 = base64url_encode(signature)
    return f"{header_b64}.{payload_b64}.{sig_b64}"

def jwt_verify(token: str) -> dict | None:
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        header_b64, payload_b64, sig_b64 = parts
        signing_input = f"{header_b64}.{payload_b64}".encode()
        # verify signature
        expected_sig = base64url_encode(hmac.new(SECRET, signing_input, hashlib.sha256).digest())
        if sig_b64 != expected_sig:
            return None
        payload = json.loads(base64url_decode(payload_b64))
        return payload
    except Exception:
        return None

class JWTandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.serve_html("<h1>JWT Auth Challenge</h1><p>Login via POST /login with username=guest&password=guest to get a token, then access /flag with your modified token.</p>")
        elif self.path == "/flag":
            auth_header = self.headers.get("Authorization", "")
            if not auth_header.startswith("Bearer "):
                self.send_error(401, "Missing Bearer token")
                return
            token = auth_header[7:]
            payload = jwt_verify(token)
            if payload is None:
                self.send_error(403, "Invalid token")
            elif payload.get("role") == "admin":
                self.send_response(200)
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                self.wfile.write(f"Flag: {FLAG}\n".encode())
            else:
                self.send_error(403, "Admin role required")
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path == "/login":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode()
            data = parse_qs(body)
            username = data.get("username", [""])[0]
            password = data.get("password", [""])[0]
            if username == "guest" and password == "guest":
                payload = {"user": "guest", "role": "user", "iat": int(time.time())}
                token = jwt_create(payload)
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"token": token}).encode())
            else:
                self.send_error(403, "Invalid credentials")
        else:
            self.send_error(404)

    def serve_html(self, html):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode())

    def log_message(self, format, *args):
        pass

if __name__ == "__main__":
    server = http.server.HTTPServer(("127.0.0.1", PORT), JWTandler)
    print(f"JWT server running on http://127.0.0.1:{PORT}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
