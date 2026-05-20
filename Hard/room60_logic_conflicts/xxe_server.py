#!/usr/bin/env python3
import http.server, sys, json, os, xml.etree.ElementTree as ET, io, urllib.parse

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 9502
ROOM_DIR = os.path.dirname(os.path.abspath(__file__))
FLAG_REAL = "THM{l0g1c_c0nfl1ct_xxe}"
FLAG_FAKE = "THM{fake_xxe_debug}"

class XXEHandler(http.server.BaseHTTPRequestHandler):
    def handle_one_request(self):
        try: super().handle_one_request()
        except (ConnectionResetError, BrokenPipeError): pass

    def do_POST(self):
        if self.path == "/parse":
            if self.headers.get("X-API-Key") != "xxe_api_key_123":
                self.send_error(403, "Invalid API key"); return
            content_length = int(self.headers.get('Content-Length',0))
            data = self.rfile.read(content_length)
            try:
                # معالج XML ضعيف يسمح بالكيانات الخارجية
                parser = ET.XMLParser(resolve_entities=True)
                doc = ET.fromstring(data, parser=parser)
                result = ET.tostring(doc, encoding='unicode')
                self._serve_text(f"Parsed: {result}")
            except ET.ParseError as e:
                self._serve_text(f"Parse error: {e}")
            except FileNotFoundError as e:
                self._serve_text(f"File not found: {e}")
            except Exception as e:
                self._serve_text(f"Error: {e}")
        else:
            self.send_error(404)

    def do_GET(self):
        if self.path == "/flag":
            if self.headers.get("X-API-Key") != "xxe_api_key_123":
                self.send_error(403); return
            self._serve_text(f"Flag: {FLAG_REAL}\n")
        else:
            self.send_error(404)

    def _serve_text(self, text):
        self.send_response(200); self.send_header("Content-type","text/plain"); self.end_headers(); self.wfile.write(text.encode())
    def log_message(self, format, *args): pass

if __name__ == "__main__":
    server = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), XXEHandler)
    print(f"XXE on {PORT}", flush=True)
    server.serve_forever()
