#!/usr/bin/env python3
import http.server, sys, json, urllib.parse, re

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8403
FLAG_REAL = "THM{ssrf_m3tadata_nosql}"
CREDS = {"admin": "Sup3rS3cr3tMetadataP@ss"}

# قاعدة بيانات وهمية (مثل MongoDB documents)
documents = [
    {"username":"flag_holder", "role":"user", "flag": FLAG_REAL},
    {"username":"guest", "role":"guest", "flag": ""},
]

class NoSQLHandler(http.server.BaseHTTPRequestHandler):
    def handle_one_request(self):
        try:
            super().handle_one_request()
        except (ConnectionResetError, BrokenPipeError):
            pass

    def do_POST(self):
        if self.path == "/api/login":
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode()
            try:
                data = json.loads(body)
            except:
                self.send_error(400); return
            user = data.get("username")
            pwd = data.get("password")
            if user == "admin" and pwd == CREDS["admin"]:
                self._serve_json({"status":"ok","token":"admin-token"})
            else:
                self.send_error(403, "Auth failed")
        elif self.path == "/api/users":
            token = self.headers.get("Authorization", "").replace("Bearer ", "")
            if token != "admin-token":
                self.send_error(403, "Unauthorized"); return
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode()
            try:
                query = json.loads(body)
            except:
                self.send_error(400); return
            # محاكاة NoSQL: تطبيق query بسيط مع دعم `$ne` و `$regex`
            results = []
            for doc in documents:
                match = True
                for key, val in query.items():
                    if isinstance(val, dict):
                        if "$ne" in val:
                            if doc.get(key) == val["$ne"]:
                                match = False
                        if "$regex" in val:
                            pattern = val["$regex"]
                            if not re.search(pattern, str(doc.get(key, "")), re.IGNORECASE):
                                match = False
                    else:
                        if doc.get(key) != val:
                            match = False
                if match:
                    results.append(doc)
            self._serve_json(results)
        else:
            self.send_error(404)

    def _serve_json(self, data):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def log_message(self, format, *args):
        pass

if __name__ == "__main__":
    server = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), NoSQLHandler)
    print(f"Admin API on {PORT}", flush=True)
    server.serve_forever()
