#!/usr/bin/env python3
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

FLAG = "THM{api_t4mper_1337}"

class APIHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        # Simple routing for /user
        if parsed.path == "/user":
            params = parse_qs(parsed.query)
            user_id = params.get('id', [''])[0]
            
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            
            if user_id == "1337":
                self.wfile.write(f"Flag: {FLAG}\n".encode())
            elif user_id == "admin":
                self.wfile.write(b"Welcome admin, nothing useful here.\n")
            else:
                self.wfile.write(b"User not found.\n")
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 9090
    server = HTTPServer(("127.0.0.1", port), APIHandler)
    print(f"API server running on http://127.0.0.1:{port}", file=sys.stderr)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
