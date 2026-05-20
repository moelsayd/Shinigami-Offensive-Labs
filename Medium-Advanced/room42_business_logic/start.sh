#!/usr/bin/env bash
ROOM="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOM"
pkill -f "python3 main_server.py 7101" 2>/dev/null
pkill -f "python3 dashboard_server.py 7102" 2>/dev/null
sleep 1
python3 main_server.py 7101 &
echo $! > .main.pid
python3 dashboard_server.py 7102 &
echo $! > .dash.pid
sleep 2
if curl -s --connect-timeout 2 http://127.0.0.1:7101/ | grep -q "BizLogic"; then
    echo "Room initialized. Discover the services."
else
    echo "Room start failed."
fi
