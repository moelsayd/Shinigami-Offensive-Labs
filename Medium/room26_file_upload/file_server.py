#!/usr/bin/env python3
import sys, os, sqlite3, subprocess, uuid, cgi, http.server
from urllib.parse import parse_qs, urlparse

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 6068
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "files.db")
conn = sqlite3.connect(DB_FILE)
conn.execute("CREATE TABLE IF NOT EXISTS uploads (id INTEGER PRIMARY KEY, uploader TEXT, filename TEXT)")
# Pre-populate with admin's backdoor file
admin_script = "print(open('supersecret/flag.txt').read())"
admin_filename = uuid.uuid4().hex[:8] + ".py"
with open(os.path.join(UPLOAD_DIR, admin_filename), "w") as f:
    f.write(admin_script)
conn.execute("INSERT OR IGNORE INTO uploads (uploader, filename) VALUES ('admin', ?)", (admin_filename,))
conn.commit()

class FileServer(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        if path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            html = """<html><body>
            <h2>Profile Picture Upload</h2>
            <form action="/upload" method="post" enctype="multipart/form-data">
            <input type="file" name="file"><br>
            <input type="submit" value="Upload">
            </form>
            <p><a href="/files">View uploaded files</a></p>
            </body></html>"""
            self.wfile.write(html.encode())
            return

        if path == "/files":
            user = query.get("user", [None])[0]
            if user is None:
                self.send_response(400)
                self.end_headers()
                return
            # Vulnerable SQL query (no sanitization)
            cursor = conn.execute(f"SELECT uploader, filename FROM uploads WHERE uploader='{user}'")
            rows = cursor.fetchall()
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            resp = "<h2>Files</h2><ul>"
            for uploader, fname in rows:
                resp += f"<li>{uploader}: {fname}</li>"
            resp += "</ul>"
            self.wfile.write(resp.encode())
            return

        if path.startswith("/uploads/"):
            fname = path.split("/")[-1]
            filepath = os.path.join(UPLOAD_DIR, fname)
            if not os.path.isfile(filepath):
                self.send_error(404)
                return
            if fname.endswith(".py"):
                try:
                    output = subprocess.check_output([sys.executable, filepath], timeout=5, stderr=subprocess.STDOUT)
                    self.send_response(200)
                    self.send_header("Content-type", "text/plain")
                    self.end_headers()
                    self.wfile.write(output)
                    return
                except Exception as e:
                    self.send_response(500)
                    self.end_headers()
                    return
            else:
                # For non-.py files, just serve raw content
                self.send_response(200)
                self.send_header("Content-type", "application/octet-stream")
                self.end_headers()
                with open(filepath, "rb") as f:
                    self.wfile.write(f.read())
                return

        self.send_error(404)

    def do_POST(self):
        if self.path == "/upload":
            content_type = self.headers.get("Content-Type", "")
            if "multipart/form-data" not in content_type:
                self.send_error(400)
                return
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={"REQUEST_METHOD": "POST", "CONTENT_TYPE": content_type}
            )
            fileitem = form["file"] if "file" in form else None
            if fileitem is None or fileitem.file is None:
                self.send_error(400, "No file uploaded")
                return

            fname = fileitem.filename
            if not fname:
                fname = "untitled"
            # Keep original extension (no filtering - misconfiguration)
            ext = os.path.splitext(fname)[1]
            new_name = uuid.uuid4().hex[:8] + ext
            filepath = os.path.join(UPLOAD_DIR, new_name)
            with open(filepath, "wb") as f:
                f.write(fileitem.file.read())

            # Record in DB with a default uploader
            uploader = "anonymous"
            conn.execute("INSERT INTO uploads (uploader, filename) VALUES (?, ?)", (uploader, new_name))
            conn.commit()

            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(f"File uploaded as {new_name}. <a href='/uploads/{new_name}'>View file</a>".encode())
        else:
            self.send_error(404)

    def log_message(self, format, *args):
        pass

if __name__ == "__main__":
    server = http.server.HTTPServer(("127.0.0.1", PORT), FileServer)
    print(f"Upload server running on http://127.0.0.1:{PORT}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    conn.close()
    server.server_close()
