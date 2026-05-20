#!/usr/bin/env bash
ROOM="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOM"
pkill -f "python3 api_server.py 7083" 2>/dev/null
sleep 1
python3 api_server.py 7083 &
echo $! > .server.pid
sleep 2
if curl -s --connect-timeout 2 http://127.0.0.1:7083/ | grep -q "API Portal"; then
    echo "Room initialized. Discover the services."
else
    echo "Room start failed. Check logs."
fi
