#!/usr/bin/env python3
import http.server, sys, json, re, urllib.parse

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8802
FLAG_REAL = "THM{c4pst0n3_ent3rpr1se_pwn3d}"
CREDS = {"admin": "NoSQL_P@ss"}

documents = [
    {"id":1,"username":"admin","role":"admin","secret":"","ssh_creds":""},
    {"id":2,"username":"dev","role":"user","secret":"","ssh_creds":""},
    {"id":3,"username":"flagowner","role":"user","secret":FLAG_REAL,"ssh_creds":"operator:0p3r4t0rP@ss"},
]

tokens = {"admin-token":"admin"}

class APIHandler(http.server.BaseHTTPRequestHandler):
    def handle_one_request(self):
        try: super().handle_one_request()
        except: pass

    def do_POST(self):
        path = urllib.parse.urlparse(self.path).path
        content_length = int(self.headers.get('Content-Length',0))
        body = self.rfile.read(content_length).decode()
        try: data = json.loads(body)
        except: self.send_error(400); return

        if path == "/api/login":
            user = data.get("username"); pwd = data.get("password")
            if user == "admin" and pwd == CREDS["admin"]:
                self._serve_json({"token":"admin-token"})
            else:
                self.send_error(403)
        elif path == "/api/query":
            token = self.headers.get("Authorization","").replace("Bearer ","")
            if token not in tokens:
                self.send_error(403); return
            query = data
            results = []
            for doc in documents:
                match = True
                for k,v in query.items():
                    if isinstance(v, dict):
                        if "$ne" in v and doc.get(k) == v["$ne"]: match = False
                        if "$regex" in v:
                            if not re.search(v["$regex"], str(doc.get(k,"")), re.IGNORECASE): match = False
                    else:
                        if doc.get(k) != v: match = False
                if match: results.append(doc)
            self._serve_json(results)
        else:
            self.send_error(404)

    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path
        qs = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        if path == "/api/profile":
            token = self.headers.get("Authorization","").replace("Bearer ","")
            if token not in tokens:
                self.send_error(403); return
            uid = qs.get('user_id',[None])[0]
            for doc in documents:
                if str(doc["id"]) == uid:
                    self._serve_json(doc); return
            self.send_error(404)
        else:
            self.send_error(404)

    def _serve_json(self, data):
        self.send_response(200); self.send_header("Content-type","application/json"); self.end_headers(); self.wfile.write(json.dumps(data).encode())
    def log_message(self, format, *args): pass

if __name__ == "__main__":
    server = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), APIHandler)
    print(f"API on {PORT}", flush=True)
    server.serve_forever()
