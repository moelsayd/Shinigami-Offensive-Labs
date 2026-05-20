#!/usr/bin/env python3
import http.server, sys, os, sqlite3, time, urllib.parse, hashlib

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 7201
ROOM_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(ROOM_DIR, "inference.db")
FLAG = "THM{bl1nd_ch4nn3ls_m4st3r}"
FAKE_FLAG = "THM{fake_inference_debug}"

# صفحة HTML ثابتة مهما كان المدخل
HTML_TEMPLATE = """<!DOCTYPE html>
<html><head><title>Internal Dashboard</title>
<style>body{background:#0a0c10;color:#c9d1d9;font-family:'Segoe UI',sans-serif;display:flex;justify-content:center;align-items:center;height:100vh;margin:0;}
.card{background:#1a1c2b;padding:2rem;border-radius:12px;box-shadow:0 0 20px rgba(0,255,0,0.2);}
h1{color:#f0883e;}p{color:#8b949e;}</style></head>
<body><div class="card"><h1>System Status</h1><p>All systems operational.</p></div></body></html>"""

ROBOTS_TXT = """User-agent: *
Disallow: /debug/
Disallow: /admin/
Disallow: /api/
"""

DEBUG_PAGE = f"""<html><body><h1>Debug Information</h1><p>Flag: {FAKE_FLAG}</p></body></html>"""

class BlindHandler(http.server.BaseHTTPRequestHandler):
    def handle_one_request(self):
        try:
            super().handle_one_request()
        except (ConnectionResetError, BrokenPipeError):
            pass

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        qs = urllib.parse.parse_qs(parsed.query)

        if path == "/":
            user_id = qs.get('id', [None])[0]
            found = False
            elapsed = 0.5  # وقت أساسي

            if user_id:
                conn = sqlite3.connect(DB_PATH)
                try:
                    # استعلام ضعيف (حقن ممكن)
                    query = f"SELECT id FROM data WHERE id = {user_id}"
                    start = time.time()
                    cursor = conn.execute(query)
                    row = cursor.fetchone()
                    end = time.time()
                    elapsed = end - start
                    found = row is not None
                except sqlite3.OperationalError as e:
                    # خطأ في SQL – نعكس ذلك أيضًا في التوقيت والكوكيز
                    elapsed = 0.2  # وقت أقل للخطأ
                    found = False
                finally:
                    conn.close()

            # إرسال الصفحة نفسها دائمًا
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            # قنوات جانبية: كوكيز ورؤوس
            self.send_header("Set-Cookie", f"found={str(found).lower()}; Path=/")
            self.send_header("X-Response-Time", f"{elapsed:.3f}")
            self.end_headers()
            self.wfile.write(HTML_TEMPLATE.encode())
        elif path == "/robots.txt":
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(ROBOTS_TXT.encode())
        elif path == "/debug/":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(DEBUG_PAGE.encode())
        else:
            self.send_error(404)

    def log_message(self, format, *args):
        pass

if __name__ == "__main__":
    server = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), BlindHandler)
    print("Server active", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
