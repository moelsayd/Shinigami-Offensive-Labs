#!/usr/bin/env python3
import http.server, sys, json, os, sqlite3, urllib.parse

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 11033
ROOM_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(ROOM_DIR, "enterprise.db")
FLAG_REAL = "THM{p3rm1ss10n_f4ilure}"

class ServiceBHandler(http.server.BaseHTTPRequestHandler):
    def handle_one_request(self):
        try: super().handle_one_request()
        except (ConnectionResetError, BrokenPipeError): pass

    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path
        qs = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        if path == "/service-b":
            token = self._get_token()
            # لا تتحقق من الصلاحيات هنا! (Permission Propagation Failure)
            user_id = qs.get('user_id', [None])[0]
            if not user_id:
                self.send_error(400, "Missing user_id"); return
            conn = sqlite3.connect(DB_PATH)
            row = conn.execute("SELECT username, role, secret FROM users WHERE id=?", (user_id,)).fetchone()
            conn.close()
            if row:
                data = {"username":row[0],"role":row[1]}
                if row[2]: data["secret"] = row[2]
                self._serve_json(data)
            else:
                self.send_error(404)
        else:
            self.send_error(404)

    def _get_token(self):
        cookie = self.headers.get('Cookie','')
        if 'token=' in cookie:
            return cookie.split('token=')[1].split(';')[0]
        return None

    def _serve_json(self, data):
        self.send_response(200); self.send_header("Content-type","application/json"); self.end_headers(); self.wfile.write(json.dumps(data).encode())
    def log_message(self, format, *args): pass

if __name__ == "__main__":
    server = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), ServiceBHandler)
    print(f"ServiceB on {PORT}", flush=True)
    server.serve_forever()
