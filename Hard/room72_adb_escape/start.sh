#!/bin/bash
ROOM="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOM"
pkill -f "web_portal.py 11201" 2>/dev/null
pkill -f "adb_sim.py 11222" 2>/dev/null
pkill -f "monitoring.py 11233" 2>/dev/null
sleep 1
python3 web_portal.py 11201 & echo $! > .portal.pid
python3 adb_sim.py 11222 & echo $! > .adb.pid
python3 monitoring.py 11233 & echo $! > .mon.pid
sleep 2
curl -s http://127.0.0.1:11201/ | grep -q "MobileCorp Portal" && echo "Room initialized. Discover the services."
