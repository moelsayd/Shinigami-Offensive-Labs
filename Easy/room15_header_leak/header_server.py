#!/usr/bin/env python3
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 5050
FLAG = "THM{header_leak}"

class HeaderLeakHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Add custom header containing the flag
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.send_header("X-Flag", FLAG)   # <-- المعلومة الحساسة في الترويسة
        self.end_headers()
        body = "<html><body><h1>Welcome to the Public Site</h1><p>Nothing to see here... or maybe check the response headers.</p></body></html>"
        self.wfile.write(body.encode())

    def log_message(self, format, *args):
        # Suppress access logs for cleanliness
        pass

if __name__ == "__main__":
    server = HTTPServer(("127.0.0.1", PORT), HeaderLeakHandler)
    print(f"Server running on http://127.0.0.1:{PORT}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
