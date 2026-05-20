#!/usr/bin/env python3
import http.server, sys, json, base64, hmac, hashlib, urllib.parse

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 13002
FLAG_PART2 = "reality_"
SECRET = b"portal_jwt_secret"

def b64e(d): return base64.urlsafe_b64encode(d).rstrip(b'=').decode()
def b64d(d):
    d += '=' * (4 - len(d) % 4)
    return base64.urlsafe_b64decode(d)
def jwt_verify(token):
    try:
        h, p, sig = token.split(".")
        header = json.loads(b64d(h))
        kid = header.get("kid","portal_key")
        if kid == "/dev/null": secret = b""
        else: secret = SECRET
        alg = header.get("alg","HS256")
        if alg == "none": return json.loads(b64d(p))
        expected = b64e(hmac.new(secret, f"{h}.{p}".encode(), hashlib.sha256).digest())
        if sig != expected: return None
        return json.loads(b64d(p))
    except: return None

class AuthHandler(http.server.BaseHTTPRequestHandler):
    def handle_one_request(self):
        try: super().handle_one_request()
        except: pass

    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path
        if path == "/auth":
            # يعطي الجزء الثاني إذا تم تقديم JWT admin
            auth = self.headers.get("Authorization","")
            token = auth.replace("Bearer ","") if auth.startswith("Bearer ") else None
            payload = jwt_verify(token) if token else None
            if not payload or payload.get("role") != "admin":
                self.send_error(403, "Admin role required"); return
            self._serve_text(FLAG_PART2)
        else:
            self.send_error(404)

    def _serve_text(self, text):
        self.send_response(200); self.send_header("Content-type","text/plain"); self.end_headers(); self.wfile.write(text.encode())
    def log_message(self, format, *args): pass

if __name__ == "__main__":
    server = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), AuthHandler)
    print(f"Auth on {PORT}", flush=True)
    server.serve_forever()
