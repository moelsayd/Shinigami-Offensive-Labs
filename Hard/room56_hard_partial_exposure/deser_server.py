#!/usr/bin/env python3
import http.server, sys, json, urllib.parse, pickle, os, io

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 9102
ROOM_DIR = os.path.dirname(os.path.abspath(__file__))
FLAG_REAL = "THM{p4rt1al_l34k_deser}"

class DeserHandler(http.server.BaseHTTPRequestHandler):
    def handle_one_request(self):
        try: super().handle_one_request()
        except (ConnectionResetError, BrokenPipeError): pass

    def do_POST(self):
        if self.path == "/process":
            # مصادقة: يتطلب X-Service-Token
            if self.headers.get("X-Service-Token") != "deser123":
                self.send_error(403, "Missing or invalid service token")
                return
            content_length = int(self.headers.get('Content-Length',0))
            data = self.rfile.read(content_length)
            try:
                obj = pickle.loads(data)
            except Exception as e:
                self.send_error(400, f"Pickle error: {e}")
                return
            # إذا كان الكائن دالة أو malicious، سيُستدعى هنا. لكننا نعيد نتيجة فقط في الحالة الآمنة.
            if isinstance(obj, dict) and 'user' in obj:
                self._serve_text(f"User info: {obj['user']}")
            else:
                self._serve_text(f"Processed: {obj}")
        else:
            self.send_error(404)

    def _serve_text(self, text):
        self.send_response(200); self.send_header("Content-type","text/plain"); self.end_headers(); self.wfile.write(text.encode())
    def log_message(self, format, *args): pass

if __name__ == "__main__":
    server = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), DeserHandler)
    print(f"Deser on {PORT}", flush=True)
    server.serve_forever()
