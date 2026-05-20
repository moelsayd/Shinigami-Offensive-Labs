#!/bin/bash
ROOM="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOM"
pkill -f "reverse_proxy.py 11381" 2>/dev/null; pkill -f "mobile_api.py 11423" 2>/dev/null; pkill -f "internal_api.py 11507" 2>/dev/null; pkill -f "worker.py 11642" 2>/dev/null; pkill -f "monitoring.py 11739" 2>/dev/null
sleep 1
python3 reverse_proxy.py 11381 & echo $! > .proxy.pid
python3 mobile_api.py 11423 & echo $! > .mob.pid
python3 internal_api.py 11507 & echo $! > .int.pid
python3 worker.py 11642 & echo $! > .work.pid
python3 monitoring.py 11739 & echo $! > .mon.pid
sleep 2
curl -s http://127.0.0.1:11381/ | grep -q "EclipseCorp Portal" && echo "Room initialized. Discover the services."
