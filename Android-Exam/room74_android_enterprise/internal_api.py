#!/usr/bin/env python3
import http.server, sys, json, os, base64, hmac, hashlib, urllib.parse, time, sqlite3

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 12033
ROOM_DIR = os.path.dirname(os.path.abspath(__file__))
FLAG_PART2 = "compromised}"
SECRET = b"android_exam_secret"

def b64e(d): return base64.urlsafe_b64encode(d).rstrip(b'=').decode()
def b64d(d):
    d += '=' * (4 - len(d) % 4)
    return base64.urlsafe_b64decode(d)
def jwt_verify(token):
    try:
        h, p, sig = token.split(".")
        header = json.loads(b64d(h))
        kid = header.get("kid","main_key")
        if kid == "/dev/null": secret = b""
        else: secret = SECRET
        alg = header.get("alg","HS256")
        if alg == "none": return json.loads(b64d(p))
        expected = b64e(hmac.new(secret, f"{h}.{p}".encode(), hashlib.sha256).digest())
        if sig != expected: return None
        return json.loads(b64d(p))
    except: return None

class InternalHandler(http.server.BaseHTTPRequestHandler):
    def handle_one_request(self):
        try: super().handle_one_request()
        except (ConnectionResetError, BrokenPipeError): pass

    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path
        auth = self.headers.get("Authorization","")
        token = auth.replace("Bearer ","") if auth.startswith("Bearer ") else None
        payload = jwt_verify(token) if token else None

        if path == "/api/user/info":
            self._serve_json({"role": payload.get("role","user") if payload else "user"})
        elif path == "/api/admin/info":
            self._serve_json({"role": "admin"})
        elif path == "/api/secret":
            if not payload or payload.get("role") != "admin":
                self.send_error(403); return
            self._serve_text(FLAG_PART2)
        elif path == "/queue":
            self._serve_json({"status":"processing","next":"/worker/status","worker":"http://127.0.0.1:12055"})
        elif path == "/worker/status":
            if self.client_address[0] != "127.0.0.1":
                self.send_error(403); return
            self._serve_json({"status":"online","endpoints":["/upload","/memory"]})
        else:
            self.send_error(404)

    def _serve_text(self, text):
        self.send_response(200); self.send_header("Content-type","text/plain"); self.end_headers(); self.wfile.write(text.encode())
    def _serve_json(self, data):
        self.send_response(200); self.send_header("Content-type","application/json"); self.end_headers(); self.wfile.write(json.dumps(data).encode())
    def log_message(self, format, *args): pass

if __name__ == "__main__":
    server = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), InternalHandler)
    print(f"Internal API on {PORT}", flush=True)
    server.serve_forever()
