#!/usr/bin/env bash
ROOM="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOM"
pkill -f "python3 api_server.py 8701" 2>/dev/null
pkill -f "python3 adb_sim.py 8702" 2>/dev/null
sleep 1
python3 api_server.py 8701 &
echo $! > .api.pid
python3 adb_sim.py 8702 &
echo $! > .adb.pid
sleep 2
if curl -s --connect-timeout 2 http://127.0.0.1:8701/ | grep -q "NeoApp Login"; then
    echo "Room initialized. Discover the services."
else
    echo "Room start failed."
fi
