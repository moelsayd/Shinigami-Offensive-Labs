#!/usr/bin/env bash
ROOM="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOM"
# تأكد من عدم وجود عمليات سابقة
pkill -f "python3 web_server.py 6088" 2>/dev/null
pkill -f "python3 ssh_server.py 6089" 2>/dev/null
sleep 1
python3 web_server.py 6088 &
echo $! > .web.pid
python3 ssh_server.py 6089 &
echo $! > .ssh.pid
sleep 2
curl -s http://127.0.0.1:6088 | grep -q "NeoCorp" && echo "✅ Web: http://localhost:6088"
nc -z 127.0.0.1 6089 && echo "✅ SSH: localhost:6089"
