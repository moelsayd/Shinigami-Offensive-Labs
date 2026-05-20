#!/usr/bin/env python3
import http.server, sys, json

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8402
FLAG_FAKE = "THM{fake_metadata_flag}"
CREDS = {"user":"admin", "password":"Sup3rS3cr3tMetadataP@ss"}

class MetadataHandler(http.server.BaseHTTPRequestHandler):
    def handle_one_request(self):
        try:
            super().handle_one_request()
        except (ConnectionResetError, BrokenPipeError):
            pass

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        data = {
            "instance-id": "i-123456",
            "user": CREDS["user"],
            "password": CREDS["password"],
            "flag": FLAG_FAKE,
            "note": "Internal API at port 8403"
        }
        self.wfile.write(json.dumps(data).encode())

    def log_message(self, format, *args):
        pass

if __name__ == "__main__":
    server = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), MetadataHandler)
    print(f"Metadata on {PORT}", flush=True)
    server.serve_forever()
