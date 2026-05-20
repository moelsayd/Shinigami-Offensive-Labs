#!/bin/bash
ROOM="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOM"
pkill -f "web_main.py 8801" 2>/dev/null; pkill -f "api_internal.py 8802" 2>/dev/null; pkill -f "ssh_sim.py 8803" 2>/dev/null
sleep 1
python3 web_main.py 8801 & echo $! > .web.pid
python3 api_internal.py 8802 & echo $! > .api.pid
python3 ssh_sim.py 8803 & echo $! > .ssh.pid
sleep 2
curl -s http://127.0.0.1:8801/ | grep -q "NeoCorp Main" && echo "Room initialized. Discover the services."
