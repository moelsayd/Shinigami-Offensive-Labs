#!/usr/bin/env bash
ROOM="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOM"
python3 race_server.py 6085 &
echo $! > .server.pid
sleep 2
curl -s http://127.0.0.1:6085 | grep -q "Restricted Login" && echo "✅ Server: http://localhost:6085"
