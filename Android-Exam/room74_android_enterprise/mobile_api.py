#!/usr/bin/env python3
import http.server, sys, json

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 12044
INTERNAL_API = "http://127.0.0.1:12033"
WORKER_API = "http://127.0.0.1:12055"

class MobileHandler(http.server.BaseHTTPRequestHandler):
    def handle_one_request(self):
        try: super().handle_one_request()
        except: pass

    def do_GET(self):
        if self.headers.get("Host") == "m.eclipse.internal":
            self.send_response(200)
            self.send_header("Content-type","application/json")
            self.end_headers()
            data = {
                "internal_api": INTERNAL_API,
                "worker_api": WORKER_API,
                "queue_endpoint": "/queue",
                "upload_endpoint": "/upload"
            }
            self.wfile.write(json.dumps(data).encode())
        else:
            self.send_error(403, "Access denied")

    def log_message(self, format, *args): pass

if __name__ == "__main__":
    server = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), MobileHandler)
    print(f"Mobile API on {PORT}", flush=True)
    server.serve_forever()
