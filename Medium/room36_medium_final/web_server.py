#!/usr/bin/env python3
import http.server, sys, sqlite3, os, xml.etree.ElementTree as ET, urllib.parse
import threading, uuid, time, json

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 6088
ROOM_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(ROOM_DIR, "secrets.db")
FLAG = "THM{medium_level_chain_complete}"
FAKE_FLAG = "THM{fake_flag_neocorp}"

# ------------------ DB Helper ------------------
def get_secret_by_id(user_id):
    conn = sqlite3.connect(DB_PATH)
    # VULNERABLE QUERY
    query = f"SELECT info FROM secrets WHERE id = {user_id}"
    try:
        row = conn.execute(query).fetchone()
        conn.close()
        return row[0] if row else None
    except Exception as e:
        conn.close()
        return f"SQL Error: {e}"

# ------------------ Session Management ------------------
sessions = {}
def create_session(user):
    sid = uuid.uuid4().hex
    sessions[sid] = user
    return sid
def get_session(sid):
    return sessions.get(sid)

# ------------------ HTML Templates (with CSS) ------------------
INDEX_HTML = """<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title>NeoCorp Portal</title>
<style>body{background:#0a0c10;color:#c9d1d9;font-family:'Segoe UI',sans-serif;margin:0;padding:0;display:flex;justify-content:center;align-items:center;height:100vh;}
.container{text-align:center;} h1{color:#f0883e;font-size:3rem;} p{color:#8b949e;}</style></head><body>
<div class="container"><h1>Welcome to NeoCorp Portal</h1><p>Secure internal access.</p></div></body></html>"""

LOGIN_PAGE = """<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Login</title>
<style>body{background:#0a0c10;display:flex;justify-content:center;align-items:center;height:100vh;margin:0;font-family:'Segoe UI',sans-serif;}
.box{background:#1a1c2b;padding:2rem;border-radius:12px;box-shadow:0 0 25px rgba(255,0,0,0.3);} h2{color:#e53170;} input{width:100%;padding:10px;margin:8px 0;background:#0d0f1a;border:1px solid #333;color:white;border-radius:5px;} input[type=submit]{background:#e53170;border:none;cursor:pointer;}
</style></head><body><div class="box"><h2>Admin Login</h2><form method="POST" action="/login"><input name="username" placeholder="Username"><br><input type="password" name="password" placeholder="Password"><br><input type="submit" value="Log In"></form>
<!-- Default creds disabled for security --></div></body></html>"""

DASHBOARD = """<html><body style="background:#0a0c10;color:#c9d1d9;font-family:'Segoe UI',sans-serif;padding:2rem;"><h2>Admin Dashboard</h2><p>Welcome, {user}.</p><div style="background:#1a1c2b;padding:1rem;border-radius:8px;"><h3>Command Exec</h3><form method="GET" action="/admin/exec"><input name="cmd" placeholder="id" style="padding:8px;background:#0d0f1a;border:1px solid #333;color:white;"><input type="submit" value="Run" style="background:#e53170;border:none;padding:8px 15px;color:white;margin-left:8px;"></form><pre>{output}</pre></div><a href="/logout" style="color:#e53170;">Logout</a></body></html>"""

class NeoCorpHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        qs = urllib.parse.parse_qs(parsed.query)
        
        if path == "/":
            self._serve_html(INDEX_HTML)
        elif path == "/assets/app.js":
            js_code = """// NeoCorp Portal 2025
const DEBUG_MODE = false;
const API_ENDPOINT = "/api/v1/data";
const DEV_PANEL = "/internal/console";
console.log("App ready");"""
            self._serve_text(js_code, "application/javascript")
        elif path == "/robots.txt":
            self._serve_text("User-agent: *\nDisallow: /backup/\nDisallow: /internal/")
        elif path == "/login":
            self._serve_html(LOGIN_PAGE)
        elif path == "/admin":
            if not self._check_auth():
                self.send_error(403); return
            self._serve_html(DASHBOARD.replace("{user}", "admin").replace("{output}", ""))
        elif path == "/admin/exec":
            if not self._check_auth():
                self.send_error(403); return
            cmd = qs.get('cmd', [''])[0]
            if cmd:
                try:
                    import subprocess
                    output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, timeout=5).decode()
                except Exception as e:
                    output = str(e)
            else:
                output = ""
            self._serve_html(DASHBOARD.replace("{user}", "admin").replace("{output}", output))
        elif path == "/api/v1/data":
            uid = qs.get('id', [''])[0]
            if not uid:
                self._serve_json({"status":"ok"})
            else:
                secret = get_secret_by_id(uid)
                if secret:
                    self._serve_json({"status":"ok","data":secret})
                else:
                    self._serve_json({"status":"ok"})
        elif path == "/internal/console":
            self._serve_json({"note":"dev panel active","file":"/backup/dev-config.old"})
        elif path == "/backup/dev-config.old":
            content = """DB_USER=admin
DB_PASS=neo123
SSH_USER=limited
SSH_PASS=limited123
NEXT_STAGE=/api/v1/internal/users
"""
            self._serve_text(content)
        elif path == "/backup/fake-flag.txt":
            self._serve_text(f"FLAG={FAKE_FLAG}")
        elif path == "/api/v1/internal/users":
            self._serve_json({"users":["admin","guest"],"flag_hint":"/api/v1/secure/flag"})
        elif path == "/api/v1/secure/flag":
            if self.headers.get('X-Role') == 'admin':
                self._serve_text(f"Flag: {FLAG}\n")
            else:
                self.send_error(403, "Forbidden")
        elif path == "/api/v1/import":
            self.send_error(405, "Use POST method")
        elif path == "/flag_hint.txt":
            self._serve_text("Hint: The final flag requires a special header: X-Role: admin")
        else:
            self.send_error(404)

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        if self.path == "/login":
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode()
            data = urllib.parse.parse_qs(body)
            user = data.get('username', [''])[0]
            pwd = data.get('password', [''])[0]
            if user == 'admin' and pwd == 'neo123':
                sid = create_session('admin')
                self.send_response(302)
                self.send_header('Set-Cookie', f'session={sid}; Path=/')
                self.send_header('Location', '/admin')
                self.end_headers()
            else:
                self.send_error(403, "Invalid credentials")
        elif self.path == "/api/v1/import":
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                xml_data = self.rfile.read(content_length)
                # Vulnerable XML parsing
                parser = ET.XMLParser(resolve_entities=True)
                root = ET.fromstring(xml_data, parser=parser)
                result = ET.tostring(root, encoding='unicode')
                self._serve_text(f"Processed: {result}")
            except Exception as e:
                self.send_error(500, str(e))
        else:
            self.send_error(404)

    def _check_auth(self):
        cookie = self.headers.get('Cookie', '')
        if 'session=' in cookie:
            sid = cookie.split('session=')[1].split(';')[0]
            return get_session(sid) is not None
        return False

    def _serve_html(self, html):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode())

    def _serve_text(self, text, content_type="text/plain"):
        self.send_response(200)
        self.send_header("Content-type", content_type)
        self.end_headers()
        self.wfile.write(text.encode())

    def _serve_json(self, data):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def log_message(self, format, *args):
        pass

if __name__ == "__main__":
    server = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), NeoCorpHandler)
    print(f"NeoCorp web on http://127.0.0.1:{PORT}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
