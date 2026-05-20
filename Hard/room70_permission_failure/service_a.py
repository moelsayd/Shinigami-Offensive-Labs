#!/usr/bin/env python3
import http.server, sys, json, os, base64, hmac, hashlib, urllib.parse

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 11022
ROOM_DIR = os.path.dirname(os.path.abspath(__file__))
SECRET_MAIN = b"secret123"  # نفس المفتاح الضعيف

def b64e(d): return base64.urlsafe_b64encode(d).rstrip(b'=').decode()
def b64d(d):
    d += '=' * (4 - len(d) % 4)
    return base64.urlsafe_b64decode(d)
def get_secret_from_kid(kid):
    if kid == "/dev/null": return b""
    if kid == "main_key": return SECRET_MAIN
    return None
def jwt_verify(token):
    try:
        h, p, sig = token.split(".")
        header = json.loads(b64d(h))
        kid = header.get("kid","main_key")
        secret = get_secret_from_kid(kid)
        if secret is None: return None
        alg = header.get("alg","HS256")
        if alg == "none": return json.loads(b64d(p))
        expected = b64e(hmac.new(secret, f"{h}.{p}".encode(), hashlib.sha256).digest())
        if sig != expected: return None
        return json.loads(b64d(p))
    except: return None

class ServiceAHandler(http.server.BaseHTTPRequestHandler):
    def handle_one_request(self):
        try: super().handle_one_request()
        except (ConnectionResetError, BrokenPipeError): pass

    def do_GET(self):
        token = self._get_token()
        payload = jwt_verify(token) if token else None
        if not payload: self.send_error(403, "Invalid token"); return
        self._serve_text(f"Your role in Service A: {payload.get('role','user')}")

    def do_POST(self):
        if self.path == "/service-a":
            token = self._get_token()
            payload = jwt_verify(token) if token else None
            if not payload: self.send_error(403); return
            # ترقية: يمكن لأي مستخدم ترقية نفسه! (Permission Propagation Failure)
            content_length = int(self.headers.get('Content-Length',0))
            body = self.rfile.read(content_length).decode()
            data = urllib.parse.parse_qs(body)
            new_role = data.get('role', ['admin'])[0]
            # تحديث قاعدة البيانات المركزية
            conn = sqlite3.connect(os.path.join(ROOM_DIR, "enterprise.db"))
            conn.execute("UPDATE users SET role=? WHERE id=?", (new_role, payload["id"]))
            conn.commit()
            conn.close()
            self._serve_text(f"Role updated to {new_role} in Service A")
        else:
            self.send_error(404)

    def _get_token(self):
        cookie = self.headers.get('Cookie','')
        if 'token=' in cookie:
            return cookie.split('token=')[1].split(';')[0]
        return None

    def _serve_text(self, text):
        self.send_response(200); self.send_header("Content-type","text/plain"); self.end_headers(); self.wfile.write(text.encode())
    def log_message(self, format, *args): pass

if __name__ == "__main__":
    server = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), ServiceAHandler)
    print(f"ServiceA on {PORT}", flush=True)
    server.serve_forever()
