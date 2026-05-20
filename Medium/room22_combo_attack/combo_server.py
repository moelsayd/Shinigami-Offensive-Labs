#!/usr/bin/env python3
import sys, json, http.server
from urllib.parse import urlparse, parse_qs

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 6063
FLAG = "THM{dir_and_param_combo}"

# قاعدة بيانات وهمية مخزنة في ملف ليكتشفه المتدرب
DB_CONTENT = """
[
  {"id":1, "name":"john", "role":"user"},
  {"id":2, "name":"admin", "role":"user"},
  {"id":"flag", "name":"flag_holder", "role":"admin"}
]
"""

class ComboHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        # الصفحة الرئيسية
        if path == "/":
            self.serve_html("<h1>Welcome to the Portal</h1><p>Nothing to see here.</p>")

        # تسريب ملف قاعدة بيانات وهمي
        elif path == "/backup/users.db":
            self.serve_json(DB_CONTENT)

        # API user – يتطلب بارامتر id
        elif path == "/api/user":
            user_id = query.get("id", [None])[0]
            if user_id is None:
                self.serve_json('{"error":"Missing id parameter"}')
            elif user_id == "1":
                self.serve_json('{"id":1, "name":"john", "role":"user"}')
            elif user_id == "2":
                self.serve_json('{"id":2, "name":"admin", "role":"user"}')
            else:
                self.serve_json('{"error":"User not found"}', code=404)

        # API admin – لا يظهر في التوثيق العادي
        elif path == "/api/admin":
            user_id = query.get("id", [None])[0]
            if user_id == "flag":
                self.serve_text(f"Flag: {FLAG}\n")
            else:
                self.serve_json('{"error":"Admin function requires correct id"}', code=403)

        else:
            self.serve_json('{"error":"Not found"}', code=404)

    def serve_html(self, html):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode())

    def serve_json(self, data, code=200):
        self.send_response(code)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(data.encode())

    def serve_text(self, text, code=200):
        self.send_response(code)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(text.encode())

    def log_message(self, format, *args):
        pass

if __name__ == "__main__":
    server = http.server.HTTPServer(("127.0.0.1", PORT), ComboHandler)
    print(f"Combo server running on http://127.0.0.1:{PORT}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
