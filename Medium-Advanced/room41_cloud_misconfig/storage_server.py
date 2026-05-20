#!/usr/bin/env python3
import http.server, sys, json, sqlite3, os, hmac, hashlib, urllib.parse

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 7085
ROOM_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(ROOM_DIR, "storage.db")
SECRET_KEY = b"abcdef1234567890abcdef1234567890abcdef12"  # من ملف .env

class StorageHandler(http.server.BaseHTTPRequestHandler):
    def handle_one_request(self):
        try:
            super().handle_one_request()
        except (ConnectionResetError, BrokenPipeError):
            pass

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        qs = urllib.parse.parse_qs(parsed.query)

        # التحقق من التوقيع (Signature V4 مبسط)
        if not self._verify_signature():
            self.send_error(403, "Signature mismatch")
            return

        if path == "/":
            self._serve_json({"bucket": "internal-data", "objects": ["flag.txt", "fake-flag.txt"]})
        elif path == "/object":
            key = qs.get('key', [''])[0]
            if not key:
                self.send_error(400, "Missing key parameter")
                return
            conn = sqlite3.connect(DB_PATH)
            row = conn.execute("SELECT value FROM objects WHERE key=?", (key,)).fetchone()
            conn.close()
            if row:
                self._serve_text(row[0])
            else:
                self.send_error(404, "Object not found")
        else:
            self.send_error(404)

    def _verify_signature(self):
        # توقيع بسيط: X-Amz-Signature = HMAC-SHA256(secret, string-to-sign)
        # string-to-sign = method + path + timestamp
        req_signature = self.headers.get('X-Amz-Signature', '')
        timestamp = self.headers.get('X-Amz-Date', '')
        if not req_signature or not timestamp:
            return False
        string_to_sign = f"GET\n{self.path}\n{timestamp}"
        expected = hmac.new(SECRET_KEY, string_to_sign.encode(), hashlib.sha256).hexdigest()
        return hmac.compare_digest(req_signature, expected)

    def _serve_json(self, data):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def _serve_text(self, text):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(text.encode())

    def log_message(self, format, *args):
        pass

if __name__ == "__main__":
    server = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), StorageHandler)
    print("Server active", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
