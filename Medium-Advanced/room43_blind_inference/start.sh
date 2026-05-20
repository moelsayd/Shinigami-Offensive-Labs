#!/usr/bin/env bash
ROOM="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOM"
pkill -f "python3 blind_server.py 7201" 2>/dev/null
sleep 1
python3 blind_server.py 7201 &
echo $! > .server.pid
sleep 2
if curl -s --connect-timeout 2 http://127.0.0.1:7201/ | grep -q "System Status"; then
    echo "Room initialized. Discover the services."
else
    echo "Room start failed. Check logs."
fi
