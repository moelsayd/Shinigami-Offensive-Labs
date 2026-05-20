#!/usr/bin/env python3
import sys, json, http.server
from urllib.parse import urlparse, parse_qs

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 6069
FLAG = "THM{internal_ep_exposed}"

# قاعدة بيانات وهمية
users = [
    {"id": 1, "name": "John Doe", "role": "user", "email": "john@example.com"},
    {"id": 2, "name": "Jane Smith", "role": "user", "email": "jane@example.com"},
    {"id": 99, "name": "Internal Admin", "role": "admin", "email": "admin@internal",
     "flag": FLAG}
]

class APIHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        query = parse_qs(parsed.query)

        # نقطة عامة
        if path == "/api/v1/users":
            self._respond_json([{"id": u["id"], "name": u["name"]} for u in users])

        # نقطة داخلية (بلا قيود وصول – misconfiguration)
        elif path == "/api/v1/internal/users":
            user_id = query.get("id", [None])[0]
            if user_id:
                # BOLA: يمكن طلب أي id بدون تحقق من الصلاحية
                for u in users:
                    if str(u["id"]) == user_id:
                        self._respond_json(u)
                        return
                self._respond_error(404, "User not found")
            else:
                self._respond_json(users)

        # نقطة تصحيح (debug) تكشف عن معلومات حساسة
        elif path == "/api/v1/debug":
            info = {
                "server": "API-Gateway v1.2",
                "internal_ip": "10.0.1.7",
                "db_host": "db.internal",
                "feature_flags": {"debug_mode": True, "expose_admin": True},
                "flag": FLAG
            }
            self._respond_json(info)

        else:
            self._respond_error(404, "Not found")

    def _respond_json(self, data):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode() + b"\n")

    def _respond_error(self, code, message):
        self.send_response(code)
        self.end_headers()
        self.wfile.write(json.dumps({"error": message}).encode())

    def log_message(self, format, *args):
        pass

if __name__ == "__main__":
    server = http.server.HTTPServer(("127.0.0.1", PORT), APIHandler)
    print(f"Internal API running on http://127.0.0.1:{PORT}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
