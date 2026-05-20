#!/usr/bin/env python3
import http.server, sys, json, os, urllib.parse, time

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 10922
ROOM_DIR = os.path.dirname(os.path.abspath(__file__))
WORKER_TOKEN = "worker_token_789"
FLAG_FAKE = "THM{fake_monitor}"

LOG_DATA = [
    "[INFO] 2026-05-15 10:00:00 Login successful for user admin",
    "[INFO] 2026-05-15 10:00:05 Transfer 500 to bob",
    "[WARN] 2026-05-15 10:00:10 Multiple transfer requests detected (possible race)",
    "[INFO] 2026-05-15 10:00:15 Monitoring service started",
    f"[SECRET] Internal worker token: {WORKER_TOKEN}",
    f"[DEBUG] Flag: {FLAG_FAKE}",
]

class MonitorHandler(http.server.BaseHTTPRequestHandler):
    def handle_one_request(self):
        try: super().handle_one_request()
        except (ConnectionResetError, BrokenPipeError): pass

    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path
        if path == "/logs":
            if self.headers.get("X-Monitor-Token") != "monitor_token_456":
                self.send_error(403, "Invalid monitor token"); return
            self._serve_text("\n".join(LOG_DATA))
        elif path == "/token":
            if self.headers.get("X-Monitor-Token") != "monitor_token_456":
                self.send_error(403); return
            self._serve_json({"worker_token": WORKER_TOKEN, "worker_endpoint": "http://127.0.0.1:10933/process"})
        else:
            self.send_error(404)

    def _serve_text(self, text):
        self.send_response(200); self.send_header("Content-type","text/plain"); self.end_headers(); self.wfile.write(text.encode())
    def _serve_json(self, data):
        self.send_response(200); self.send_header("Content-type","application/json"); self.end_headers(); self.wfile.write(json.dumps(data).encode())
    def log_message(self, format, *args): pass

if __name__ == "__main__":
    server = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), MonitorHandler)
    print(f"Monitor on {PORT}", flush=True)
    server.serve_forever()
