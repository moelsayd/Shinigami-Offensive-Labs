#!/usr/bin/env python3
import http.server, sys, json, sqlite3, os, urllib.parse

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 7102
ROOM_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(ROOM_DIR, "business.db")

class DashboardHandler(http.server.BaseHTTPRequestHandler):
    def handle_one_request(self):
        try:
            super().handle_one_request()
        except (ConnectionResetError, BrokenPipeError):
            pass

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        qs = urllib.parse.parse_qs(parsed.query)

        if path == "/dashboard":
            key = qs.get('key', [''])[0]
            if not key:
                self.send_error(403, "Missing API key")
                return
            conn = sqlite3.connect(DB_PATH)
            user = conn.execute("SELECT id, role FROM users WHERE api_key=?", (key,)).fetchone()
            if not user:
                conn.close()
                self.send_error(403, "Invalid API key")
                return
            user_id = qs.get('id', [str(user[0])])[0]
            # IDOR: أي مستخدم يمكنه جلب بيانات مستخدم آخر
            data = conn.execute("SELECT u.username, u.plan, s.data FROM users u LEFT JOIN secrets s ON u.id = s.id WHERE u.id=?", (user_id,)).fetchone()
            conn.close()
            if data:
                response = f"User: {data[0]}, Plan: {data[1]}"
                if data[2]:
                    response += f", Secret: {data[2]}"
                self._serve_text(response)
            else:
                self.send_error(404, "User not found")
        else:
            self.send_error(404)

    def _serve_text(self, text):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(text.encode())

    def log_message(self, format, *args):
        pass

if __name__ == "__main__":
    server = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), DashboardHandler)
    print("Server active", flush=True)
    server.serve_forever()
