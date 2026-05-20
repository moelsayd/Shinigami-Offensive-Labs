#!/usr/bin/env python3
import http.server, sys, json, os, urllib.parse, uuid, time, sqlite3

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 13003
ROOM_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(ROOM_DIR, "blackbox.db")
FLAG_PART3 = "mastered_"

class UserHandler(http.server.BaseHTTPRequestHandler):
    def handle_one_request(self):
        try: super().handle_one_request()
        except: pass

    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path
        qs = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        if path == "/users/profile":
            # IDOR: يعيد بيانات أي مستخدم بدون تحقق
            uid = qs.get('id', [None])[0]
            if not uid: self.send_error(400); return
            conn = sqlite3.connect(DB_PATH)
            row = conn.execute("SELECT username, role FROM users WHERE id=?", (uid,)).fetchone()
            conn.close()
            if row:
                data = {"username":row[0],"role":row[1]}
                if int(uid) == 3: data["note"] = FLAG_PART3  # مستخدم خاص يحمل الجزء الثالث
                self._serve_json(data)
            else: self.send_error(404)
        elif path == "/users/pdf":
            # ميزة PDF تسمح بجلب URL (SSRF)
            url = qs.get('url', [None])[0]
            if not url: self.send_error(400); return
            self._serve_text(f"PDF generated from {url}. Content: [Simulated]")
        else:
            self.send_error(404)

    def _serve_json(self, data):
        self.send_response(200); self.send_header("Content-type","application/json"); self.end_headers(); self.wfile.write(json.dumps(data).encode())
    def _serve_text(self, text):
        self.send_response(200); self.send_header("Content-type","text/plain"); self.end_headers(); self.wfile.write(text.encode())
    def log_message(self, format, *args): pass

if __name__ == "__main__":
    server = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), UserHandler)
    print(f"User on {PORT}", flush=True)
    server.serve_forever()
