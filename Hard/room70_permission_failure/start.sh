#!/bin/bash
ROOM="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOM"
pkill -f "reverse_proxy.py 11001" 2>/dev/null; pkill -f "service_a.py 11022" 2>/dev/null; pkill -f "service_b.py 11033" 2>/dev/null; pkill -f "monitoring.py 11044" 2>/dev/null
sleep 1
python3 reverse_proxy.py 11001 & echo $! > .proxy.pid
python3 service_a.py 11022 & echo $! > .a.pid
python3 service_b.py 11033 & echo $! > .b.pid
python3 monitoring.py 11044 & echo $! > .mon.pid
sleep 2
curl -s http://127.0.0.1:11001/ | grep -q "Enterprise Portal" && echo "Room initialized. Discover the services."
