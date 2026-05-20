#!/usr/bin/env python3
import http.server, sys, os, sqlite3, uuid, subprocess, urllib.parse, re, io, base64, time, json

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 7301
ROOM_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(ROOM_DIR, "uploads")
DB_PATH = os.path.join(ROOM_DIR, "files.db")
FLAG_REAL = "THM{upload_ch4in_rce}"
FLAG_FAKE = "THM{fake_upload_admin}"

os.makedirs(UPLOAD_DIR, exist_ok=True)

# إعداد قاعدة البيانات
conn = sqlite3.connect(DB_PATH)
conn.execute("CREATE TABLE IF NOT EXISTS files (id INTEGER PRIMARY KEY, original_name TEXT, stored_name TEXT, uploader TEXT)")
conn.execute("INSERT OR IGNORE INTO files (original_name, stored_name, uploader) VALUES ('secret.txt', 'dummy', 'admin')")
conn.commit()
conn.close()

# ------------------ تحليل multipart/form-data يدوياً ------------------
def parse_multipart(body, boundary):
    """استخراج الحقول والملفات من جسم الطلب multipart."""
    parts = body.split(b'--' + boundary.encode())
    fields = {}
    files = {}
    for part in parts[1:-1]:  # تجاهل البداية والنهاية الفارغة
        if b'\r\n\r\n' not in part:
            continue
        header_section, content = part.split(b'\r\n\r\n', 1)
        # إزالة \r\n الزائدة في النهاية
        content = content.rstrip(b'\r\n--')
        headers = {}
        for line in header_section.split(b'\r\n'):
            if b':' in line:
                key, val = line.decode(errors='ignore').split(':', 1)
                headers[key.strip().lower()] = val.strip()
        disposition = headers.get('content-disposition', '')
        name_match = re.search(r'name="([^"]+)"', disposition)
        if not name_match:
            continue
        name = name_match.group(1)
        filename_match = re.search(r'filename="([^"]+)"', disposition)
        if filename_match:
            files[name] = (filename_match.group(1), content)
        else:
            fields[name] = content.decode(errors='ignore')
    return fields, files

# ------------------ HTML ------------------
INDEX_HTML = """<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><title>Image Hosting</title>
<style>body{background:#0a0c10;color:#c9d1d9;font-family:'Segoe UI',sans-serif;display:flex;justify-content:center;align-items:center;height:100vh;margin:0;}
.card{background:#1a1c2b;padding:2rem;border-radius:12px;box-shadow:0 0 20px rgba(255,0,0,0.3);}
h2{color:#e53170;} input{width:100%;padding:10px;margin:8px 0;background:#0d0f1a;border:1px solid #333;color:white;border-radius:5px;}
input[type=submit]{background:#e53170;border:none;cursor:pointer;font-weight:bold;}
a{color:#58a6ff;}</style></head><body><div class="card">
<h2>Upload Profile Picture</h2>
<form action="/upload" method="post" enctype="multipart/form-data">
<input type="file" name="file" accept="image/*"><br>
<input type="text" name="uploader" placeholder="Your name"><br>
<input type="submit" value="Upload">
</form>
<br><a href="/files">View uploaded files</a></div></body></html>"""

ROBOTS_TXT = """User-agent: *
Disallow: /admin-login/
Disallow: /uploads/
"""

ADMIN_LOGIN_PAGE = """<html><head><title>Admin Login</title>
<style>body{background:#0a0c10;display:flex;justify-content:center;align-items:center;height:100vh;font-family:'Segoe UI',sans-serif;}
.box{background:#1a1c2b;padding:2rem;border-radius:12px;} h2{color:#00ff00;}
input{width:100%;padding:10px;margin:8px 0;background:#0d0f1a;border:1px solid #333;color:white;border-radius:5px;}
input[type=submit]{background:#00aa00;border:none;cursor:pointer;}</style></head><body>
<div class="box"><h2>Admin Login</h2><form method="POST" action="/admin-login">
<input name="username" placeholder="Username"><br>
<input type="password" name="password" placeholder="Password"><br>
<input type="submit" value="Log In"></form>
</div></body></html>"""

class UploadHandler(http.server.BaseHTTPRequestHandler):
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
            self._serve_html(INDEX_HTML)
        elif path == "/robots.txt":
            self._serve_text(ROBOTS_TXT)
        elif path == "/admin-login/":
            self._serve_html(ADMIN_LOGIN_PAGE)
        elif path == "/files":
            uploader = qs.get('uploader', [None])[0]
            if uploader:
                conn = sqlite3.connect(DB_PATH)
                try:
                    query = f"SELECT original_name, stored_name FROM files WHERE uploader = '{uploader}'"
                    rows = conn.execute(query).fetchall()
                except Exception as e:
                    rows = []
                finally:
                    conn.close()
                output = "<h2>Files</h2><ul>"
                for orig, stored in rows:
                    output += f"<li>{orig} → <a href='/uploads/{stored}'>{stored}</a></li>"
                output += "</ul>"
                self._serve_html(output)
            else:
                self._serve_text("Please provide uploader parameter. E.g., ?uploader=admin")
        elif path.startswith("/uploads/"):
            file_name = path.split("/")[-1]
            filepath = os.path.join(UPLOAD_DIR, file_name)
            if not os.path.isfile(filepath):
                self.send_error(404, "File not found")
                return
            if file_name.endswith(".py"):
                try:
                    result = subprocess.check_output(
                        [sys.executable, filepath],
                        timeout=5, stderr=subprocess.STDOUT
                    )
                    self._serve_text(result.decode())
                except subprocess.CalledProcessError as e:
                    self._serve_text(e.output.decode())
                except Exception as e:
                    self.send_error(500, str(e))
            else:
                self._serve_file(filepath)
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path == "/admin-login":
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode()
            data = urllib.parse.parse_qs(body)
            username = data.get('username', [''])[0]
            password = data.get('password', [''])[0]
            if username == 'admin' and password == 'admin123':
                self._serve_text(f"Welcome admin! Flag: {FLAG_FAKE}")
            else:
                self.send_error(403, "Wrong credentials")

        elif self.path == "/upload":
            content_type = self.headers.get("Content-Type", "")
            if "multipart/form-data" not in content_type:
                self.send_error(400, "Bad content type")
                return
            # استخراج boundary
            boundary = content_type.split("boundary=")[1] if "boundary=" in content_type else None
            if not boundary:
                self.send_error(400, "Missing boundary")
                return
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            fields, files = parse_multipart(body, boundary)

            uploader = fields.get('uploader', 'anonymous')
            if 'file' not in files:
                self.send_error(400, "No file uploaded")
                return
            original_filename, file_content = files['file']
            if not original_filename:
                original_filename = "untitled"

            # تجاوز MIME: لا نتحقق من النوع الحقيقي؛ نعتمد فقط على الامتداد كما في السيناريو المطلوب
            ext = os.path.splitext(original_filename)[1]
            stored_name = uuid.uuid4().hex[:12] + ext
            filepath = os.path.join(UPLOAD_DIR, stored_name)
            with open(filepath, "wb") as f:
                f.write(file_content)

            conn = sqlite3.connect(DB_PATH)
            conn.execute("INSERT INTO files (original_name, stored_name, uploader) VALUES (?, ?, ?)",
                         (original_filename, stored_name, uploader))
            conn.commit()
            conn.close()

            self._serve_text(f"File uploaded: {stored_name}. Access at /uploads/{stored_name}")

        else:
            self.send_error(404)

    def _serve_html(self, html):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode())

    def _serve_text(self, text):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(text.encode())

    def _serve_file(self, filepath):
        content_type = "application/octet-stream"
        if filepath.endswith(".html"):
            content_type = "text/html"
        elif filepath.endswith(".txt"):
            content_type = "text/plain"
        self.send_response(200)
        self.send_header("Content-type", content_type)
        self.end_headers()
        with open(filepath, "rb") as f:
            self.wfile.write(f.read())

    def log_message(self, format, *args):
        pass

if __name__ == "__main__":
    server = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), UploadHandler)
    print("Server active", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
