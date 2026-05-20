#!/usr/bin/env bash
ROOM="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOM"
pkill -f "python3 web_server.py 8401" 2>/dev/null
pkill -f "python3 metadata_server.py 8402" 2>/dev/null
pkill -f "python3 admin_api.py 8403" 2>/dev/null
sleep 1
python3 web_server.py 8401 & echo $! > .web.pid
python3 metadata_server.py 8402 & echo $! > .meta.pid
python3 admin_api.py 8403 & echo $! > .admin.pid
sleep 2
if curl -s --connect-timeout 2 http://127.0.0.1:8401/ | grep -q "CloudSync Portal"; then
    echo "Room initialized. Discover the services."
else
    echo "Room start failed."
fi
