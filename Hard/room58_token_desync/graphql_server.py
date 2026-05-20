#!/usr/bin/env python3
import http.server, sys, json, os, re, base64, hmac, hashlib, urllib.parse

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 9302
ROOM_DIR = os.path.dirname(os.path.abspath(__file__))
SECRET = b"graphql_secret_key"
FLAG_REAL = "THM{gr4phql_d3sync}"

# محاكاة Schema
SCHEMA = {
    "User": {"name": "String!", "role": "String!", "flag": "String"},
    "Query": {"user": "User"}
}

def jwt_verify(token):
    def b64d(d):
        d += '=' * (4 - len(d) % 4)
        return base64.urlsafe_b64decode(d)
    try:
        h, p, sig = token.split(".")
        expected = base64.urlsafe_b64encode(hmac.new(SECRET, f"{h}.{p}".encode(), hashlib.sha256).digest()).rstrip(b'=').decode()
        if sig != expected: return None
        return json.loads(b64d(p))
    except: return None

class GraphQLHandler(http.server.BaseHTTPRequestHandler):
    def handle_one_request(self):
        try: super().handle_one_request()
        except (ConnectionResetError, BrokenPipeError): pass

    def do_POST(self):
        if self.path == "/graphql":
            content_length = int(self.headers.get('Content-Length',0))
            body = self.rfile.read(content_length).decode()
            try: data = json.loads(body)
            except: self.send_error(400); return
            query = data.get("query", "")
            token = self.headers.get("Authorization","").replace("Bearer ","")

            # إذا كان استفسار Introspection
            if "introspection" in query.lower() or "__schema" in query:
                result = {"data": {"__schema": {"types": [{"name":"User","fields":[{"name":"name"},{"name":"role"},{"name":"flag"}]}]}}}
                self._send_json(result)
                return

            # للاستفسار العادي
            if "user" in query:
                payload = jwt_verify(token) if token else None
                if not payload:
                    self._send_json({"errors":[{"message":"Authentication required"}]})
                    return
                # هنا الثغرة: نعيد flag لأي مستخدم تم التحقق من توقيعه فقط (لا نتحقق من role)
                user_data = {"name": payload.get("user","unknown"), "role": payload.get("role","user")}
                # إذا طلب flag، نعطيه
                if "flag" in query:
                    user_data["flag"] = FLAG_REAL
                result = {"data": {"user": user_data}}
                self._send_json(result)
                return

            self._send_json({"errors":[{"message":"Invalid query"}]})
        else:
            self.send_error(404)

    def _send_json(self, data):
        self.send_response(200); self.send_header("Content-type","application/json"); self.end_headers(); self.wfile.write(json.dumps(data).encode())
    def log_message(self, format, *args): pass

if __name__ == "__main__":
    server = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), GraphQLHandler)
    print(f"GraphQL on {PORT}", flush=True)
    server.serve_forever()
