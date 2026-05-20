#!/usr/bin/env python3
import http.server, sys, json, os, base64, hmac, hashlib, time

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 10820
ROOM_DIR = os.path.dirname(os.path.abspath(__file__))
SECRET = b"secret_metadata_key"
FLAG_REAL = "THM{ssrf_gr4ph_p1v0t}"  # ليس هنا، لكن نضعه لخداع
FAKE_FLAG = "THM{fake_metadata}"

def b64e(d): return base64.urlsafe_b64encode(d).rstrip(b'=').decode()
def b64d(d):
    d += '=' * (4 - len(d) % 4)
    return base64.urlsafe_b64decode(d)
def jwt_create(payload, secret=SECRET, kid="metadata_key", alg="HS256"):
    header = {"alg":alg,"typ":"JWT","kid":kid}
    h = b64e(json.dumps(header).encode())
    p = b64e(json.dumps(payload).encode())
    sig = b64e(hmac.new(secret, f"{h}.{p}".encode(), hashlib.sha256).digest())
    return f"{h}.{p}.{sig}"

class MetadataHandler(http.server.BaseHTTPRequestHandler):
    def handle_one_request(self):
        try: super().handle_one_request()
        except (ConnectionResetError, BrokenPipeError): pass

    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path
        if path == "/":
            token = jwt_create({"role":"user", "iat":int(time.time())})
            data = {
                "token": token,
                "api_endpoint": "http://127.0.0.1:10833",
                "note": "Internal API requires valid JWT"
            }
            self._serve_json(data)
        elif path == "/logs":
            self._serve_text("[ACCESS] 2026-05-15 10:00:00 internal_api:10833 - 200 OK\n[ACCESS] 2026-05-15 10:00:01 metadata:10820 - 200 OK")
        else:
            self.send_error(404)

    def _serve_text(self, text):
        self.send_response(200); self.send_header("Content-type","text/plain"); self.end_headers(); self.wfile.write(text.encode())
    def _serve_json(self, data):
        self.send_response(200); self.send_header("Content-type","application/json"); self.end_headers(); self.wfile.write(json.dumps(data).encode())
    def log_message(self, format, *args): pass

if __name__ == "__main__":
    server = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), MetadataHandler)
    print(f"Metadata on {PORT}", flush=True)
    server.serve_forever()
