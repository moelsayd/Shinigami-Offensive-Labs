#!/usr/bin/env python3
import http.server, sys, json, bcrypt, os

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 13005
ROOM_DIR = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(ROOM_DIR, "hashes.txt")) as f:
    lines = f.read().splitlines()
    HASH_LEGACY = lines[1].split(":")[1].encode()  # legacy hash

class LegacyHandler(http.server.BaseHTTPRequestHandler):
    def handle_one_request(self):
        try: super().handle_one_request()
        except: pass

    def do_GET(self):
        if self.path == "/legacy/v1/export":
            auth = self.headers.get("Authorization","")
            if auth.startswith("Bearer "):
                pwd = auth[7:]
                if bcrypt.checkpw(pwd.encode(), HASH_LEGACY):
                    self._serve_text("SHINIGAMI{")  # الجزء الأول من العلم (ليس موجودًا، لكن للتوضيح)
                    return
            # ثغرة: إذا تم إرسال X-Legacy-Auth: admin يتجاوز
            if self.headers.get("X-Legacy-Auth") == "admin":
                self._serve_text("SHINIGAMI{")
            else:
                self.send_error(403)
        else:
            self.send_error(404)

    def _serve_text(self, text):
        self.send_response(200); self.send_header("Content-type","text/plain"); self.end_headers(); self.wfile.write(text.encode())
    def log_message(self, format, *args): pass

if __name__ == "__main__":
    server = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), LegacyHandler)
    print(f"Legacy on {PORT}", flush=True)
    server.serve_forever()
