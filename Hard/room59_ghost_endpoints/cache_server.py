#!/usr/bin/env python3
import http.server, sys, json, os, urllib.parse, re

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 9402
ROOM_DIR = os.path.dirname(os.path.abspath(__file__))
FLAG_REAL = "THM{gh0st_c4che_xss}"
FLAG_FAKE = "THM{fake_cache_data}"

# تخزين "مخبأ" بسيط
cache_store = {}

class CacheHandler(http.server.BaseHTTPRequestHandler):
    def handle_one_request(self):
        try: super().handle_one_request()
        except (ConnectionResetError, BrokenPipeError): pass

    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path
        api_key = self.headers.get("X-API-Key")
        host = self.headers.get("Host","")

        # محاكاة Cache Poisoning: إذا كان Host يحتوي على "evil"، نُخدع ونُعيد العلم
        if path == "/cache/data":
            if api_key != "ghost_api_key_123":
                self.send_error(403, "Invalid API key")
                return
            # إنشاء مفتاح للمخبأ بناءً على Host
            cache_key = f"{host}-data"
            if cache_key in cache_store:
                self._serve_text(cache_store[cache_key])
                return
            # استجابة عادية
            data = {"status":"ok","data":FLAG_FAKE}
            cache_store[cache_key] = json.dumps(data)
            self._serve_json(data)
        elif path == "/flag":
            # نقطة مخفية لا تظهر إلا إذا كان المخبأ مسمومًا
            if api_key != "ghost_api_key_123":
                self.send_error(403); return
            self._serve_text(f"Real flag: {FLAG_REAL}\n")
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path == "/cache/poison":
            # محاكاة تسميم المخبأ: يمكن لأي شخص أن يرسل Host مع "evil" لإنشاء إدخال ضار
            host = self.headers.get("Host","")
            if "evil" in host:
                cache_store[f"{host}-data"] = json.dumps({"status":"ok","data":FLAG_REAL})
                self._serve_text("Cache poisoned")
            else:
                self.send_error(400, "Host must contain 'evil'")
        else:
            self.send_error(404)

    def _serve_text(self, text):
        self.send_response(200); self.send_header("Content-type","text/plain"); self.end_headers(); self.wfile.write(text.encode())
    def _serve_json(self, data):
        self.send_response(200); self.send_header("Content-type","application/json"); self.end_headers(); self.wfile.write(json.dumps(data).encode())
    def log_message(self, format, *args): pass

if __name__ == "__main__":
    server = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), CacheHandler)
    print(f"Cache API on {PORT}", flush=True)
    server.serve_forever()
