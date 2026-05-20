#!/usr/bin/env bash
ROOM="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOM"
pkill -f "python3 web_server.py 7084" 2>/dev/null
pkill -f "python3 storage_server.py 7085" 2>/dev/null
sleep 1
python3 web_server.py 7084 &
echo $! > .web.pid
python3 storage_server.py 7085 &
echo $! > .storage.pid
sleep 2
if curl -s --connect-timeout 2 http://127.0.0.1:7084/ | grep -q "Cloud Corp"; then
    echo "Room initialized. Discover the services."
else
    echo "Room start failed. Check logs."
fi
