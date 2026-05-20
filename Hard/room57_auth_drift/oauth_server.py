#!/usr/bin/env python3
import http.server, sys, urllib.parse, json, uuid

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 9202
AUTH_CODES = {}

class OAuthHandler(http.server.BaseHTTPRequestHandler):
    def handle_one_request(self):
        try: super().handle_one_request()
        except: pass

    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path
        qs = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        if path == "/auth":
            client_id = qs.get('client_id',[''])[0]
            redirect_uri = qs.get('redirect_uri',[''])[0]
            state = qs.get('state',[''])[0]
            # قبول أي redirect_uri (ثغرة)
            code = f"oauth_code_user_{uuid.uuid4().hex[:8]}"
            AUTH_CODES[code] = "user"
            location = f"{redirect_uri}?code={code}"
            if state: location += f"&state={state}"
            self.send_response(302)
            self.send_header("Location", location)
            self.end_headers()
        else:
            self.send_error(404)

if __name__ == "__main__":
    server = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), OAuthHandler)
    print(f"OAuth on {PORT}", flush=True)
    server.serve_forever()
