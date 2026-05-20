#!/usr/bin/env bash
ROOM="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOM"
python3 web_server.py 6084 &
echo $! > .server.pid
sleep 2
curl -s http://127.0.0.1:6084 | grep -q "File Server" && echo "✅ Server: http://localhost:6084"
