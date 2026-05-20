#!/usr/bin/env python3
import http.server, sys, json, os, base64, hmac, hashlib, urllib.parse, time

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 10833
ROOM_DIR = os.path.dirname(os.path.abspath(__file__))
FAKE_FLAG = "THM{fake_internal_api}"
DB_TOKEN = "db_admin_token_123"

def b64e(d): return base64.urlsafe_b64encode(d).rstrip(b'=').decode()
def b64d(d):
    d += '=' * (4 - len(d) % 4)
    return base64.urlsafe_b64decode(d)
def get_secret_from_kid(kid):
    if kid == "/dev/null": return b""
    if kid == "metadata_key": return b"secret_metadata_key"
    return None
def jwt_verify(token):
    try:
        h, p, sig = token.split(".")
        header = json.loads(b64d(h))
        kid = header.get("kid", "metadata_key")
        secret = get_secret_from_kid(kid)
        if secret is None: return None
        alg = header.get("alg","HS256")
        if alg == "none": return json.loads(b64d(p))
        expected = b64e(hmac.new(secret, f"{h}.{p}".encode(), hashlib.sha256).digest())
        if sig != expected: return None
        return json.loads(b64d(p))
    except: return None

rate_limit = {}

class APIHandler(http.server.BaseHTTPRequestHandler):
    def handle_one_request(self):
        try: super().handle_one_request()
        except (ConnectionResetError, BrokenPipeError): pass

    def do_GET(self):
        client_ip = self.client_address[0]
        now = time.time()
        rate_limit.setdefault(client_ip, []).append(now)
        rate_limit[client_ip] = [t for t in rate_limit[client_ip] if now - t < 10]
        if len(rate_limit[client_ip]) > 20:
            self.send_error(429, "Rate limit exceeded"); return

        path = urllib.parse.urlparse(self.path).path
        auth = self.headers.get("Authorization","")
        if path == "/api/user":
            token = auth.replace("Bearer ","") if auth.startswith("Bearer ") else None
            payload = jwt_verify(token) if token else None
            if not payload:
                self.send_error(403, "Invalid token"); return
            self._serve_json({"username":"admin","role":payload.get("role","user"),"info":"This is a normal user"})
        elif path == "/api/admin/db_token":
            token = auth.replace("Bearer ","") if auth.startswith("Bearer ") else None
            payload = jwt_verify(token) if token else None
            if not payload or payload.get("role") != "admin":
                self.send_error(403, "Admin role required"); return
            self._serve_json({"db_token": DB_TOKEN, "db_endpoint": "http://127.0.0.1:10847"})
        else:
            self.send_error(404)

    def _serve_json(self, data):
        self.send_response(200); self.send_header("Content-type","application/json"); self.end_headers(); self.wfile.write(json.dumps(data).encode())
    def log_message(self, format, *args): pass

if __name__ == "__main__":
    server = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), APIHandler)
    print(f"API on {PORT}", flush=True)
    server.serve_forever()
