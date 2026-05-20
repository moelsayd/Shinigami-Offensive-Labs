#!/usr/bin/env python3
import http.server, sys, json, os, base64, hmac, hashlib, urllib.parse

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 10202
ROOM_DIR = os.path.dirname(os.path.abspath(__file__))
FLAG_REAL = "THM{m1cr0_id_c0nfus10n}"
FLAG_FAKE = "THM{fake_internal_flag}"

def b64e(d): return base64.urlsafe_b64encode(d).rstrip(b'=').decode()
def b64d(d):
    d += '=' * (4 - len(d) % 4)
    return base64.urlsafe_b64decode(d)

def get_secret_from_kid(kid):
    """يستخرج المفتاح السري من ملف (ثغرة kid injection)."""
    if kid == "/dev/null":
        return b""   # مفتاح فارغ!
    # قائمة مفاتيح آمنة
    if kid == "main_key":
        return b"main_secret_123"
    return None

def jwt_verify_kid(token):
    try:
        h, p, sig = token.split(".")
        header = json.loads(b64d(h))
        alg = header.get("alg", "HS256")
        kid = header.get("kid", "main_key")
        secret = get_secret_from_kid(kid)
        if secret is None:
            return None
        if alg == "none":
            return json.loads(b64d(p))
        expected = b64e(hmac.new(secret, f"{h}.{p}".encode(), hashlib.sha256).digest())
        if sig != expected:
            return None
        return json.loads(b64d(p))
    except:
        return None

class InternalHandler(http.server.BaseHTTPRequestHandler):
    def handle_one_request(self):
        try: super().handle_one_request()
        except (ConnectionResetError, BrokenPipeError): pass

    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path
        if path == "/internal/admin/flag":
            auth = self.headers.get("Authorization","")
            if not auth.startswith("Bearer "):
                self.send_error(403, "Missing token"); return
            token = auth[7:]
            payload = jwt_verify_kid(token)
            if not payload:
                self.send_error(403, "Invalid token"); return
            if payload.get("role") != "admin":
                self.send_error(403, "Admin role required"); return
            self._serve_text(f"Flag: {FLAG_REAL}\n")
        elif path == "/":
            self._serve_text("Internal API. Use /internal/admin/flag with valid token.")
        else:
            self.send_error(404)

    def _serve_text(self, text):
        self.send_response(200); self.send_header("Content-type","text/plain"); self.end_headers(); self.wfile.write(text.encode())
    def log_message(self, format, *args): pass

if __name__ == "__main__":
    server = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), InternalHandler)
    print(f"Internal API on {PORT}", flush=True)
    server.serve_forever()
