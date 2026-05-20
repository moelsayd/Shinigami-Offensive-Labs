#!/usr/bin/env python3
import http.server, sys, json, os, urllib.parse, yaml, threading

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 9802
ROOM_DIR = os.path.dirname(os.path.abspath(__file__))
FLAG_REAL = "THM{c0ntext_y4ml_pp}"

class YAMLHandler(http.server.BaseHTTPRequestHandler):
    def handle_one_request(self):
        try: super().handle_one_request()
        except (ConnectionResetError, BrokenPipeError): pass

    def do_POST(self):
        if self.path == "/process":
            if self.headers.get("X-API-Key") != "yaml_api_key_789":
                self.send_error(403, "Invalid API key"); return
            content_length = int(self.headers.get('Content-Length',0))
            data = self.rfile.read(content_length)
            try:
                obj = yaml.load(data, Loader=yaml.Loader)  # غير آمن
                self._serve_text(f"Processed: {obj}")
            except yaml.YAMLError as e:
                self._serve_text(f"YAML error: {e}")
        else:
            self.send_error(404)

    def do_GET(self):
        if self.path == "/flag":
            if self.headers.get("X-API-Key") != "yaml_api_key_789":
                self.send_error(403); return
            self._serve_text(f"Flag: {FLAG_REAL}\n")
        else:
            self.send_error(404)

    def _serve_text(self, text):
        self.send_response(200); self.send_header("Content-type","text/plain"); self.end_headers(); self.wfile.write(text.encode())
    def log_message(self, format, *args): pass

if __name__ == "__main__":
    server = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), YAMLHandler)
    print(f"YAML on {PORT}", flush=True)
    server.serve_forever()
