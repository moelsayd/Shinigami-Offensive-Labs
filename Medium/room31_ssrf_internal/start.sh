#!/usr/bin/env bash
ROOM="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOM"
python3 internal_admin.py 6083 & echo $! > .pid_int
python3 web_server.py 6082 & echo $! > .pid_web
sleep 2
curl -s http://127.0.0.1:6082 | grep -q "Login" && echo "✅ Main server: http://localhost:6082"
curl -s http://127.0.0.1:6083/admin | grep -q "THM" && echo "✅ Internal service: 127.0.0.1:6083"
