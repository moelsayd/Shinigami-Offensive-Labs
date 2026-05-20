#!/usr/bin/env python3
import http.server, sys, json, os, time, uuid, threading, sqlite3, base64, hmac, hashlib

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 11642
ROOM_DIR = os.path.dirname(os.path.abspath(__file__))
FLAG_PART2 = "inference_mastered}"
SECRET_WORKER = b"worker_secret_456"   # مفتاح مختلف للـ worker

def b64e(d): return base64.urlsafe_b64encode(d).rstrip(b'=').decode()
def b64d(d):
    d += '=' * (4 - len(d) % 4)
    return base64.urlsafe_b64decode(d)
def jwt_verify_worker(token):
    try:
        h, p, sig = token.split(".")
        header = json.loads(b64d(h))
        kid = header.get("kid","worker_key")
        if kid == "/dev/null": secret = b""
        elif kid == "worker_key": secret = SECRET_WORKER
        else: return None
        alg = header.get("alg","HS256")
        if alg == "none": return json.loads(b64d(p))
        expected = b64e(hmac.new(secret, f"{h}.{p}".encode(), hashlib.sha256).digest())
        if sig != expected: return None
        return json.loads(b64d(p))
    except: return None

# قائمة مهام وهمية
task_queue = []
memory_state = {}  # حالة الذاكرة

def process_tasks():
    while True:
        if task_queue:
            task = task_queue.pop(0)
            # معالجة: إذا كان الملف يحتوي على "admin_pipeline"، نُسجّل العلم
            if b"admin_pipeline" in task["content"]:
                memory_state[task["id"]] = FLAG_PART2
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
        path = urllib.parse.urlparse(self.path).path
        if path == "/memory":
            auth = self.headers.get("Authorization","")
            token = auth.replace("Bearer ","") if auth.startswith("Bearer ") else None
            payload = jwt_verify_worker(token) if token else None
            if not payload or payload.get("role") != "admin":
                self.send_error(403, "Admin role required for worker memory"); return
            # إرجاع حالة الذاكرة
            self._serve_json(memory_state)
        elif path == "/status":
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
