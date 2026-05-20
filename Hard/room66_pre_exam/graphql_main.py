#!/usr/bin/env python3
import http.server, sys, json, os, urllib.parse, uuid, time, sqlite3, threading, re, pickle, urllib.request, urllib.error

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 10101
ROOM_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(ROOM_DIR, "ambiguous.db")
INTERNAL_WORKER = "http://localhost:10102/process"
FLAG_FAKE = "THM{fake_graphql_flag}"

# Schema GraphQL
SCHEMA = {
    "__schema": {
        "queryType": {"name": "Query"},
        "mutationType": {"name": "Mutation"},
        "types": [
            {"name":"User","fields":[{"name":"id"},{"name":"username"},{"name":"role"},{"name":"flag"}]},
            {"name":"Task","fields":[{"name":"id"},{"name":"command"},{"name":"status"}]},
            {"name":"Query","fields":[{"name":"user"},{"name":"tasks"}]},
            {"name":"Mutation","fields":[{"name":"createTask"},{"name":"updateUserRole"}]},
        ]
    },
    "user": {"id":1,"username":"admin","role":"user","flag":FLAG_FAKE},
    "tasks": []
}

# قائمة مهام غير متزامنة
task_queue = []
task_results = {}

def async_worker():
    while True:
        if task_queue:
            task = task_queue.pop(0)
            # معالجة المهمة: إذا كان الأمر يبدأ بـ "PICKLE:" نعالج الـ pickle
            cmd = task["command"]
            if cmd.startswith("PICKLE:"):
                data = cmd[7:]
                try:
                    obj = pickle.loads(bytes.fromhex(data))
                    result = f"Executed: {obj}"
                except Exception as e:
                    result = f"Error: {e}"
            else:
                result = f"Command not recognized: {cmd}"
            task_results[task["id"]] = result
            # تحديث قاعدة البيانات
            conn = sqlite3.connect(DB_PATH)
            conn.execute("UPDATE tasks SET status=? WHERE id=?", (result, task["id"]))
            conn.commit()
            conn.close()
        time.sleep(2)  # معالجة دورية

threading.Thread(target=async_worker, daemon=True).start()

LOGIN_HTML = """<!DOCTYPE html>
<html><head><title>Ambiguous Corp</title>
<style>body{background:#0a0c10;color:#c9d1d9;font-family:'Segoe UI',sans-serif;display:flex;justify-content:center;align-items:center;height:100vh;margin:0;}
.box{background:#1a1c2b;padding:2rem;border-radius:12px;} h2{color:#e53170;}
input{width:100%;padding:10px;margin:8px 0;background:#0d0f1a;border:1px solid #333;color:white;border-radius:5px;}
input[type=submit]{background:#e53170;border:none;cursor:pointer;font-weight:bold;}
</style></head><body><div class="box"><h2>Login</h2>
<form method="POST" action="/login"><input name="username" placeholder="Username"><br>
<input type="password" name="password" placeholder="Password"><br>
<input type="submit" value="Log In"></form>
</div></body></html>"""

ROBOTS_TXT = """User-agent: *
Disallow: /graphql
Disallow: /debug
Disallow: /admin
"""

DEBUG_PAGE = json.dumps({"status":"ok","fake_flag":FLAG_FAKE})

sessions = {}

class GraphQLHandler(http.server.BaseHTTPRequestHandler):
    def handle_one_request(self):
        try: super().handle_one_request()
        except (ConnectionResetError, BrokenPipeError): pass

    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path
        qs = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)

        if path == "/":
            self._serve_html(LOGIN_HTML)
        elif path == "/robots.txt":
            self._serve_text(ROBOTS_TXT)
        elif path == "/debug":
            self._serve_json(DEBUG_PAGE)
        elif path == "/graphql":
            query = qs.get('query', [None])[0]
            if not query:
                self._serve_text("Use POST for GraphQL queries, or provide ?query= for GET")
                return
            self._handle_graphql(query, None)
        elif path == "/proxy":
            url = qs.get('url', [None])[0]
            if not url:
                self.send_error(400, "Missing url parameter")
                return
            # فلتر SSRF غير متناسق: يمنع localhost و 127.0.0.1 لكن يسمح ببعض التمثيلات
            hostname = urllib.parse.urlparse(url).hostname
            if hostname in ["localhost", "127.0.0.1", "0.0.0.0"]:
                self.send_error(403, "Internal hosts blocked")
                return
            try:
                req = urllib.request.Request(url)
                with urllib.request.urlopen(req, timeout=5) as resp:
                    data = resp.read().decode()
                self._serve_text(data)
            except Exception as e:
                self._serve_text(f"Proxy error: {e}")
        elif path == "/dashboard":
            token = self._get_cookie('token')
            if not token or token not in sessions:
                self.send_error(403); return
            user = sessions[token]
            html = f"<h2>Dashboard</h2><p>Welcome {user['username']}, role: {user['role']}</p>"
            if user['role'] == 'admin':
                html += "<p>Access admin GraphQL playground at <a href='/graphql'>/graphql</a></p>"
            self._serve_html(html)
        elif path == "/logout":
            self.send_response(302)
            self.send_header("Set-Cookie","token=; expires=Thu, 01 Jan 1970 00:00:00 GMT")
            self.send_header("Location","/"); self.end_headers()
        else:
            self.send_error(404)

    def do_POST(self):
        path = urllib.parse.urlparse(self.path).path
        content_length = int(self.headers.get('Content-Length',0))
        body = self.rfile.read(content_length).decode()

        if path == "/login":
            data = urllib.parse.parse_qs(body)
            user = data.get('username',[''])[0]; pwd = data.get('password',[''])[0]
            conn = sqlite3.connect(DB_PATH)
            row = conn.execute("SELECT id, username, role FROM users WHERE username=? AND password=?", (user,pwd)).fetchone()
            conn.close()
            if row:
                sid = uuid.uuid4().hex
                sessions[sid] = {"id":row[0],"username":row[1],"role":row[2]}
                self.send_response(302)
                self.send_header("Set-Cookie", f"token={sid}; Path=/")
                self.send_header("Location", "/dashboard"); self.end_headers()
            else:
                self.send_error(403, "Invalid credentials")
        elif path == "/graphql":
            self._handle_graphql(None, body)
        else:
            self.send_error(404)

    def _handle_graphql(self, query, body):
        if body:
            try:
                data = json.loads(body)
                query = data.get("query","")
                variables = data.get("variables",{})
            except:
                self.send_error(400); return
        else:
            variables = {}

        # معالجة Introspection
        if "introspection" in query.lower() or "__schema" in query:
            self._serve_json({"data": SCHEMA})
            return

        # معالجة user query
        if "user" in query:
            uid = 1  # default
            self._serve_json({"data": {"user": SCHEMA["user"]}})
            return

        # معالجة Mutation createTask
        if "createTask" in query and "command" in query:
            cmd = variables.get("command","") or "default"
            task_id = uuid.uuid4().hex[:8]
            task = {"id": task_id, "command": cmd, "status": "pending"}
            task_queue.append(task)
            conn = sqlite3.connect(DB_PATH)
            conn.execute("INSERT INTO tasks (id, command, status) VALUES (?,?,?)", (task_id, cmd, "pending"))
            conn.commit()
            conn.close()
            self._serve_json({"data": {"createTask": {"id": task_id, "command": cmd, "status": "pending"}}})
            return

        # معالجة Mutation updateUserRole (ثغرة: لا تحقق من صلاحيات)
        if "updateUserRole" in query:
            new_role = variables.get("role","user")
            uid = variables.get("userId",1)
            conn = sqlite3.connect(DB_PATH)
            conn.execute("UPDATE users SET role=? WHERE id=?", (new_role, uid))
            conn.commit()
            conn.close()
            self._serve_json({"data": {"updateUserRole": {"id": uid, "role": new_role}}})
            return

        self._serve_json({"errors":[{"message":"Invalid query"}]})

    def _get_cookie(self, key):
        cookie = self.headers.get('Cookie','')
        if f'{key}=' in cookie:
            return cookie.split(f'{key}=')[1].split(';')[0]
        return None

    def _serve_html(self, html):
        self.send_response(200); self.send_header("Content-type","text/html"); self.end_headers(); self.wfile.write(html.encode())
    def _serve_text(self, text):
        self.send_response(200); self.send_header("Content-type","text/plain"); self.end_headers(); self.wfile.write(text.encode())
    def _serve_json(self, data):
        self.send_response(200); self.send_header("Content-type","application/json"); self.end_headers(); self.wfile.write(json.dumps(data).encode())
    def log_message(self, format, *args): pass

if __name__ == "__main__":
    server = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), GraphQLHandler)
    print(f"GraphQL on {PORT}", flush=True)
    server.serve_forever()
