#!/usr/bin/env bash
ROOM_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOM_DIR"
python3 web_server.py 6072 &
echo $! > .web.pid
python3 ssh_simulator.py 6073 &
echo $! > .ssh.pid
sleep 2
curl -s http://127.0.0.1:6072 | grep -q "Internal Portal" && echo "✅ Web server: http://localhost:6072"
nc -z 127.0.0.1 6073 && echo "✅ SSH simulator: localhost:6073"
