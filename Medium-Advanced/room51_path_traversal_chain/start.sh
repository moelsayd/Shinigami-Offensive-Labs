#!/usr/bin/env bash
ROOM="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOM"
pkill -f "python3 web_server.py 8501" 2>/dev/null
pkill -f "python3 admin_api.py 8502" 2>/dev/null
sleep 1
python3 web_server.py 8501 & echo $! > .web.pid
python3 admin_api.py 8502 & echo $! > .api.pid
sleep 2
if curl -s --connect-timeout 2 http://127.0.0.1:8501/ | grep -q "Document Server"; then
    echo "Room initialized. Discover the services."
else
    echo "Room start failed."
fi
