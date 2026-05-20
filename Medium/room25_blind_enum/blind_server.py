#!/usr/bin/env python3
import sys
import http.server
from urllib.parse import urlparse, parse_qs

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 6067
FLAG = "THM{blind_err0r_enum}"

users = {
    "1": {"name": "John", "role": "user"},
    "2": {"name": "Jane", "role": "user"},
    "admin": {"name": "Administrator", "role": "admin", "flag": FLAG}
}

class BlindHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

#        if path == "/":
#            self.send_response(200)
#            self.send_header("Content-type", "text/html")
#            self.end_headers()
#            self.wfile.write(b"<h1>API</h1><p>Try <a href='/user?id=1'>/user?id=1</a></p>")
#            return

        if path == "/user":
            user_id = query.get("id", [None])[0]
            if user_id is None:
                self.send_error(400, "Missing id parameter")
                return

            if "'" in user_id and not user_id.endswith("'"):
                self.send_response(500)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(b"<h2>Database Error</h2><p>Unclosed quotation mark after the character string. Check your syntax.</p>")
                return

            if "'" in user_id and ("--" in user_id or "OR" in user_id.upper() or "=" in user_id):
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                resp = "<h2>All Users</h2><ul>"
                for uid, u in users.items():
                    resp += f"<li>{u['name']} ({u['role']})</li>"
                    if uid == "admin":
                        resp += f"<li>Flag: {u.get('flag', '')}</li>"
                resp += "</ul>"
                self.wfile.write(resp.encode())
                return

            if user_id in users:
                user = users[user_id]
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                body = f"<h2>User Found</h2><p>Name: {user['name']}<br>Role: {user['role']}</p>"
                self.wfile.write(body.encode())
            else:
                self.send_response(404)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(b"<h2>User not found</h2>")
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass

if __name__ == "__main__":
    server = http.server.HTTPServer(("127.0.0.1", PORT), BlindHandler)
    print(f"Blind server running on http://127.0.0.1:{PORT}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
