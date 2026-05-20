#!/usr/bin/env python3
import http.server, sys, json, os, urllib.parse, uuid, time

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 9401
ROOM_DIR = os.path.dirname(os.path.abspath(__file__))
FLAG_FAKE = "THM{fake_ghost_portal}"
API_KEY = "ghost_api_key_123"  # مطلوب للخدمة الداخلية

INDEX_HTML = """<!DOCTYPE html>
<html><head><title>GhostCorp Portal</title>
<style>body{background:#0a0c10;color:#c9d1d9;font-family:'Segoe UI',sans-serif;padding:2rem;}
h1{color:#f0883e;} a{color:#58a6ff;}</style></head><body>
<h1>GhostCorp Internal Portal</h1>
<p>Welcome. This system adapts to your actions.</p>
<script>
// DOM-based XSS: يعكس معامل url من الرابط
const params = new URLSearchParams(window.location.search);
const redirect = params.get('redirect');
if (redirect) {
    document.getElementById('dynamic').innerHTML = '<a href="' + redirect + '">Click here</a>';
}
</script>
<div id="dynamic"></div>
<!-- Try /init with X-Init header first -->
</body></html>"""

ROBOTS_TXT = """User-agent: *
Disallow: /config
Disallow: /admin
"""

CONFIG_JSON = json.dumps({
    "api_key": API_KEY,
    "internal_service": "http://localhost:9402",
    "note": "Cache service at /cache requires valid Host header"
})

DEBUG_PAGE = """<html><body><h1>Debug Info</h1><p>API Key: {}</p></body></html>""".format(API_KEY)

# تتبّع من قام بزيارة /init
initialized_sessions = set()

class GhostHandler(http.server.BaseHTTPRequestHandler):
    def handle_one_request(self):
        try: super().handle_one_request()
        except (ConnectionResetError, BrokenPipeError): pass

    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path
        qs = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        cookie = self.headers.get('Cookie','')
        session_id = None
        if 'session=' in cookie:
            session_id = cookie.split('session=')[1].split(';')[0]

        if path == "/":
            self._serve_html(INDEX_HTML)
        elif path == "/robots.txt":
            self._serve_text(ROBOTS_TXT)
        elif path == "/config":
            self._serve_json(CONFIG_JSON)
        elif path == "/init":
            # يجب إرسال هيدر X-Init لتوثيق الطلب
            if self.headers.get("X-Init") == "true":
                session_id = uuid.uuid4().hex
                initialized_sessions.add(session_id)
                self.send_response(302)
                self.send_header("Set-Cookie", f"session={session_id}; Path=/")
                self.send_header("Location", "/debug")
                self.end_headers()
            else:
                self.send_error(403, "Missing X-Init header")
        elif path == "/debug":
            if session_id and session_id in initialized_sessions:
                self._serve_html(DEBUG_PAGE)
            else:
                self.send_error(403, "Not initialized. Send POST /init with X-Init: true first")
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path == "/init":
            if self.headers.get("X-Init") == "true":
                session_id = uuid.uuid4().hex
                initialized_sessions.add(session_id)
                self.send_response(200)
                self.send_header("Set-Cookie", f"session={session_id}; Path=/")
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                self.wfile.write(b"Initialized. Now access /debug")
            else:
                self.send_error(403, "Missing X-Init header")
        else:
            self.send_error(404)

    def _serve_html(self, html):
        self.send_response(200); self.send_header("Content-type","text/html"); self.end_headers(); self.wfile.write(html.encode())
    def _serve_text(self, text):
        self.send_response(200); self.send_header("Content-type","text/plain"); self.end_headers(); self.wfile.write(text.encode())
    def _serve_json(self, data):
        self.send_response(200); self.send_header("Content-type","application/json"); self.end_headers(); self.wfile.write(json.dumps(data).encode())
    def log_message(self, format, *args): pass

if __name__ == "__main__":
    server = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), GhostHandler)
    print(f"Ghost web on {PORT}", flush=True)
    server.serve_forever()
