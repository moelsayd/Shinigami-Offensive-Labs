#!/usr/bin/env python3
import http.server, sys, json, urllib.parse

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 10847
FLAG_REAL = "THM{ssrf_gr4ph_p1v0t}"

class DBHandler(http.server.BaseHTTPRequestHandler):
    def handle_one_request(self):
        try: super().handle_one_request()
        except (ConnectionResetError, BrokenPipeError): pass

    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path
        qs = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        if path == "/query":
            token = qs.get('token', [None])[0]
            if token != "db_admin_token_123":
                self.send_error(403, "Invalid DB token"); return
            key = qs.get('key', [None])[0]
            if key == "flag":
                self._serve_text(FLAG_REAL)
            else:
                self._serve_text("Key not found")
        else:
            self.send_error(404)

    def _serve_text(self, text):
        self.send_response(200); self.send_header("Content-type","text/plain"); self.end_headers(); self.wfile.write(text.encode())
    def log_message(self, format, *args): pass

if __name__ == "__main__":
    server = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), DBHandler)
    print(f"DB on {PORT}", flush=True)
    server.serve_forever()
