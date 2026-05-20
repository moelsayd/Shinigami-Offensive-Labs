#!/usr/bin/env bash
ROOM="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOM"
pkill -f "python3 web_server.py 7080" 2>/dev/null
sleep 1
python3 web_server.py 7080 &
echo $! > .server.pid
sleep 2
if curl -s --connect-timeout 2 http://127.0.0.1:7080/ | grep -q "NeoCorp"; then
    echo "Room initialized. Discover the services."
else
    echo "Room start failed. Check logs."
fi
