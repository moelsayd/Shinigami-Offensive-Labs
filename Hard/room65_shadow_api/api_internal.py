#!/usr/bin/env python3
import http.server, sys, json, urllib.parse, sqlite3, os

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 10020
ROOM_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(ROOM_DIR, "shadow.db")
FLAG_REAL = "THM{sh4d0w_4pi_pr0t0_poll}"

# محاكاة Prototype Pollution
config = {"role": "user", "debug": False}

class APIHandler(http.server.BaseHTTPRequestHandler):
    def handle_one_request(self):
        try: super().handle_one_request()
        except (ConnectionResetError, BrokenPipeError): pass

    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path
        qs = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)

        if path == "/docs":
            self._serve_json({"endpoints": ["/api/users", "/api/user/{id}", "/api/updateConfig", "/api/flag"]})
        elif path == "/api/users":
            conn = sqlite3.connect(DB_PATH)
            users = conn.execute("SELECT id, username, role FROM users").fetchall()
            conn.close()
            self._serve_json([{"id":u[0],"username":u[1],"role":u[2]} for u in users])
        elif path.startswith("/api/user/"):
            user_id = path.split("/")[-1]
            conn = sqlite3.connect(DB_PATH)
            row = conn.execute("SELECT id, username, role, secret FROM users WHERE id=?", (user_id,)).fetchone()
            conn.close()
            if row:
                data = {"id":row[0],"username":row[1],"role":row[2]}
                if row[3]: data["secret"] = row[3]
                self._serve_json(data)
            else: self.send_error(404)
        elif path == "/api/flag":
            if config.get("role") != "admin":
                self.send_error(403, "Admin role required")
                return
            self._serve_text(f"Flag: {FLAG_REAL}")
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path == "/api/updateConfig":
            content_length = int(self.headers.get('Content-Length',0))
            body = self.rfile.read(content_length).decode()
            try:
                data = json.loads(body)
            except:
                self.send_error(400); return
            # Prototype Pollution: تحديث الكائن مباشرة دون فلتر
            for key, value in data.items():
                config[key] = value
            self._serve_json({"status":"ok","config":config})
        else:
            self.send_error(404)

    def _serve_text(self, text):
        self.send_response(200); self.send_header("Content-type","text/plain"); self.end_headers(); self.wfile.write(text.encode())
    def _serve_json(self, data):
        self.send_response(200); self.send_header("Content-type","application/json"); self.end_headers(); self.wfile.write(json.dumps(data).encode())
    def log_message(self, format, *args): pass

if __name__ == "__main__":
    server = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), APIHandler)
    print(f"API on {PORT}", flush=True)
    server.serve_forever()
