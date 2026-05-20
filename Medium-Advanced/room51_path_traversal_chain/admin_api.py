#!/usr/bin/env python3
import http.server, sys, json, urllib.parse, re, time

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8502
FLAG_REAL = "THM{path_to_nosql_chain}"
CREDS = {"admin": "NoSQL_P@ssw0rd!"}

# البيانات (تحاكي NoSQL documents)
documents = [
    {"username":"flag_holder","role":"admin","secret": FLAG_REAL},
    {"username":"guest","role":"user","secret": "nothing"},
    {"username":"tester","role":"user","secret": "test_data"},
]

class NoSQLAPIHandler(http.server.BaseHTTPRequestHandler):
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
                self._serve_json({"status":"ok","token":"admin-jwt-token"})
            else:
                self.send_error(403, "Auth failed")
        elif self.path == "/api/query":
            token = self.headers.get("Authorization", "").replace("Bearer ", "")
            if token != "admin-jwt-token":
                self.send_error(403, "Unauthorized"); return
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode()
            try:
                query = json.loads(body)
            except:
                self.send_error(400); return
            # فلترة باستخدام NoSQL-like operators
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
                        if "$gt" in val:
                            if not str(doc.get(key)) > str(val["$gt"]):
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
    server = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), NoSQLAPIHandler)
    print(f"Admin API on {PORT}", flush=True)
    server.serve_forever()
