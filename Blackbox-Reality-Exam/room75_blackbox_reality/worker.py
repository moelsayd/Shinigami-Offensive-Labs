#!/usr/bin/env python3
import http.server, sys, json, os, time, uuid, threading, sqlite3

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 13006
ROOM_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(ROOM_DIR, "blackbox.db")
FLAG_FINAL_PIECE = "SHINIGAMI{blackbox_reality_mastered}"  # العلم الكامل يستخدم كمرجع

task_queue = []
memory_state = {}

def process_tasks():
    while True:
        if task_queue:
            task = task_queue.pop(0)
            if b"admin_pipeline" in task["content"]:
                memory_state[task["id"]] = FLAG_FINAL_PIECE
            else:
                memory_state[task["id"]] = "processed"
        time.sleep(2)

threading.Thread(target=process_tasks, daemon=True).start()

class WorkerHandler(http.server.BaseHTTPRequestHandler):
    def handle_one_request(self):
        try: super().handle_one_request()
        except (ConnectionResetError, BrokenPipeError): pass

    def do_POST(self):
        if self.path == "/upload":
            content_length = int(self.headers.get('Content-Length',0))
            data = self.rfile.read(content_length)
            task_id = uuid.uuid4().hex[:8]
            task_queue.append({"id":task_id,"content":data})
            self._serve_json({"status":"queued","task_id":task_id})
        else:
            self.send_error(404)

    def do_GET(self):
        if self.path == "/memory":
            # يتطلب رمز JWT من نوع خاص (worker_secret)
            auth = self.headers.get("Authorization","")
            if auth == "Bearer worker_admin_token":
                self._serve_json(memory_state)
            else:
                self.send_error(403)
        elif self.path == "/status":
            self._serve_text("Worker active")
        else:
            self.send_error(404)

    def _serve_text(self, text):
        self.send_response(200); self.send_header("Content-type","text/plain"); self.end_headers(); self.wfile.write(text.encode())
    def _serve_json(self, data):
        self.send_response(200); self.send_header("Content-type","application/json"); self.end_headers(); self.wfile.write(json.dumps(data).encode())
    def log_message(self, format, *args): pass

if __name__ == "__main__":
    server = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), WorkerHandler)
    print(f"Worker on {PORT}", flush=True)
    server.serve_forever()
