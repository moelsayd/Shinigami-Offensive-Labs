#!/usr/bin/env python3
import http.server, sys, json, pickle, os, urllib.parse

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 10933
ROOM_DIR = os.path.dirname(os.path.abspath(__file__))
FLAG_REAL = "THM{r4c3_l0g1c_hybr1d}"

class WorkerHandler(http.server.BaseHTTPRequestHandler):
    def handle_one_request(self):
        try: super().handle_one_request()
        except (ConnectionResetError, BrokenPipeError): pass

    def do_POST(self):
        if self.path == "/process":
            if self.headers.get("X-Worker-Token") != "worker_token_789":
                self.send_error(403, "Invalid worker token"); return
            content_length = int(self.headers.get('Content-Length',0))
            data = self.rfile.read(content_length)
            try:
                obj = pickle.loads(data)
                self._serve_text(f"Result: {obj}")
            except Exception as e:
                self._serve_text(f"Error: {e}")
        else:
            self.send_error(404)

    def do_GET(self):
        if self.path == "/flag":
            if self.headers.get("X-Worker-Token") != "worker_token_789":
                self.send_error(403); return
            self._serve_text(FLAG_REAL)
        else:
            self.send_error(404)

    def _serve_text(self, text):
        self.send_response(200); self.send_header("Content-type","text/plain"); self.end_headers(); self.wfile.write(text.encode())
    def log_message(self, format, *args): pass

if __name__ == "__main__":
    server = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), WorkerHandler)
    print(f"Worker on {PORT}", flush=True)
    server.serve_forever()
