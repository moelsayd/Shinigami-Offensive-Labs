#!/usr/bin/env python3
import http.server, sys

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 6083
FLAG = "THM{ssrf_byp4ss_intern4l}"

class InternalAdmin(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/admin":
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(f"Internal Admin Panel\nFlag: {FLAG}\n".encode())
        else:
            self.send_error(404)

    def log_message(self, f, *a): pass

server = http.server.HTTPServer(("127.0.0.1", PORT), InternalAdmin)
print(f"Internal admin running on 127.0.0.1:{PORT}", flush=True)
server.serve_forever()
