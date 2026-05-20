#!/usr/bin/env python3
import http.server, sys, json, urllib.parse, sqlite3, os

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 13004
ROOM_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(ROOM_DIR, "blackbox.db")

class BillingHandler(http.server.BaseHTTPRequestHandler):
    def handle_one_request(self):
        try: super().handle_one_request()
        except: pass

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length',0))
        body = self.rfile.read(content_length).decode()
        data = urllib.parse.parse_qs(body)
        path = urllib.parse.urlparse(self.path).path
        if path == "/billing/refund":
            amount = int(data.get('amount', ['0'])[0])
            # ثغرة منطقية: مبلغ سالب يزيد الرصيد
            conn = sqlite3.connect(DB_PATH)
            conn.execute("INSERT INTO transactions (user, amount, status) VALUES ('guest', ?, 'refunded')", (amount,))
            conn.commit()
            conn.close()
            self._serve_json({"status":"refunded","amount":amount})
        elif path == "/billing/audit":
            conn = sqlite3.connect(DB_PATH)
            rows = conn.execute("SELECT * FROM transactions").fetchall()
            conn.close()
            self._serve_json([{"id":r[0],"user":r[1],"amount":r[2],"status":r[3]} for r in rows])
        else:
            self.send_error(404)

    def do_GET(self):
        if self.path == "/billing/flag":
            # يتطلب ترخيص خاص (رأس X-Finance-Admin)
            if self.headers.get("X-Finance-Admin") == "true":
                self._serve_text("2026}")
            else:
                self.send_error(403)
        else:
            self.send_error(404)

    def _serve_json(self, data):
        self.send_response(200); self.send_header("Content-type","application/json"); self.end_headers(); self.wfile.write(json.dumps(data).encode())
    def _serve_text(self, text):
        self.send_response(200); self.send_header("Content-type","text/plain"); self.end_headers(); self.wfile.write(text.encode())
    def log_message(self, format, *args): pass

if __name__ == "__main__":
    server = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), BillingHandler)
    print(f"Billing on {PORT}", flush=True)
    server.serve_forever()
