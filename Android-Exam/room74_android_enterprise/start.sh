#!/bin/bash
ROOM="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOM"
pkill -f "reverse_proxy.py 12001" 2>/dev/null; pkill -f "adb_sim.py 12022" 2>/dev/null; pkill -f "internal_api.py 12033" 2>/dev/null; pkill -f "mobile_api.py 12044" 2>/dev/null; pkill -f "worker.py 12055" 2>/dev/null; pkill -f "monitoring.py 12066" 2>/dev/null
sleep 1
python3 reverse_proxy.py 12001 & echo $! > .proxy.pid
python3 adb_sim.py 12022 & echo $! > .adb.pid
python3 internal_api.py 12033 & echo $! > .api.pid
python3 mobile_api.py 12044 & echo $! > .mob.pid
python3 worker.py 12055 & echo $! > .work.pid
python3 monitoring.py 12066 & echo $! > .mon.pid
sleep 2
curl -s http://127.0.0.1:12001/ | grep -q "Eclipse Mobile Enterprise" && echo "Room initialized. Discover the services."
