#!/usr/bin/env python3
import http.server, sys, base64, os
from Crypto.Cipher import AES

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 9602
KEY = b'secretkey1234567'[:16]
FLAG_REAL = "THM{p4dd1ng_0r4cl3_f1le}"

class OracleHandler(http.server.BaseHTTPRequestHandler):
    def handle_one_request(self):
        try: super().handle_one_request()
        except (ConnectionResetError, BrokenPipeError): pass

    def do_POST(self):
        if self.path == "/decrypt":
            if self.headers.get("X-API-Key") != "oracle_api_key_456":
                self.send_error(403); return
            content_length = int(self.headers.get('Content-Length',0))
            raw = self.rfile.read(content_length)
            try:
                data = base64.b64decode(raw.decode())
                iv, ct = data[:16], data[16:]
                cipher = AES.new(KEY, AES.MODE_CBC, iv)
                dec = cipher.decrypt(ct)
                # التحقق من padding
                padlen = dec[-1]
                if padlen < 1 or padlen > 16 or dec[-padlen:] != bytes([padlen]*padlen):
                    self.send_response(403)
                    self.send_header("Content-type","text/plain")
                    self.end_headers()
                    self.wfile.write(b"Padding error")
                    return
                # إزالة padding
                plain = dec[:-padlen]
                if plain == FLAG_REAL.encode():
                    self._serve_text(f"Flag: {FLAG_REAL}")
                else:
                    self._serve_text(f"Decrypted (hex): {plain.hex()}")
            except Exception as e:
                self.send_error(400, "Bad input")
        else:
            self.send_error(404)

    def _serve_text(self, text):
        self.send_response(200); self.send_header("Content-type","text/plain"); self.end_headers(); self.wfile.write(text.encode())
    def log_message(self, format, *args): pass

if __name__ == "__main__":
    server = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), OracleHandler)
    print(f"Oracle on {PORT}", flush=True)
    server.serve_forever()
