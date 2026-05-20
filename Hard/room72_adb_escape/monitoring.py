#!/usr/bin/env python3
import http.server, sys, json

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 11233
FLAG_FAKE = "THM{fake_monitor_adb}"

LOGS = [
    "[INFO] 2026-05-18 14:00:00 User admin logged into portal",
    "[WARN] 2026-05-18 14:00:05 JWT kid validation failed – possible injection attempt",
    "[INFO] 2026-05-18 14:00:10 ADB connection from 192.168.1.100",
    f"[DEBUG] Flag: {FLAG_FAKE}",
]

class MonitorHandler(http.server.BaseHTTPRequestHandler):
    def handle_one_request(self):
        try: super().handle_one_request()
        except (ConnectionResetError, BrokenPipeError): pass

    def do_GET(self):
        if self.path == "/logs":
            self._serve_text("\n".join(LOGS))
        else:
            self.send_error(404)

    def _serve_text(self, text):
        self.send_response(200); self.send_header("Content-type","text/plain"); self.end_headers(); self.wfile.write(text.encode())
    def log_message(self, format, *args): pass

if __name__ == "__main__":
    server = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), MonitorHandler)
    print(f"Monitor on {PORT}", flush=True)
    server.serve_forever()
