#!/usr/bin/env python3
import sys, json, http.server

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 6065
FLAG = "THM{m4ss_ass1gn_4pi}"

class MassAssignmentHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == "/register":
            content_length = int(self.headers.get('Content-Length', 0))
            raw = self.rfile.read(content_length)
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                self.send_error(400, "Bad JSON")
                return

            # المطور نسي يحدد الحقول المسموح بها
            user = data.get("user", "unknown")
            role = data.get("role", "user")

            response = {"status": "ok", "message": f"User '{user}' registered with role '{role}'."}
            if role == "admin":
                response["flag"] = FLAG

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_error(404)

    def log_message(self, format, *args):
        pass

if __name__ == "__main__":
    server = http.server.HTTPServer(("127.0.0.1", PORT), MassAssignmentHandler)
    print(f"Mass assignment server running on http://127.0.0.1:{PORT}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
