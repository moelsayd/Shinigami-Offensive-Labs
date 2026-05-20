#!/usr/bin/env bash
ROOM="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOM"
pkill -f "python3 race_server.py 8601" 2>/dev/null
sleep 1
python3 race_server.py 8601 &
echo $! > .server.pid
sleep 2
if curl -s --connect-timeout 2 http://127.0.0.1:8601/ | grep -q "Employee Portal"; then
    echo "Room initialized. Discover the services."
else
    echo "Room start failed."
fi
