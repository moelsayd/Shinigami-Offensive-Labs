#!/usr/bin/env bash
ROOM="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOM"
pkill -f "python3 upload_server.py 7301" 2>/dev/null
sleep 1
python3 upload_server.py 7301 &
echo $! > .server.pid
sleep 2
if curl -s --connect-timeout 2 http://127.0.0.1:7301/ | grep -q "Upload Profile"; then
    echo "Room initialized. Discover the services."
else
    echo "Room start failed. Check logs."
fi
