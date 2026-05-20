#!/bin/bash
ROOM="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOM"
pkill -f "web_main.py 8901" 2>/dev/null; pkill -f "api_server.py 8902" 2>/dev/null; pkill -f "ssh_sim.py 8903" 2>/dev/null
sleep 1
python3 web_main.py 8901 & echo $! > .web.pid
python3 api_server.py 8902 & echo $! > .api.pid
python3 ssh_sim.py 8903 & echo $! > .ssh.pid
sleep 2
curl -s http://127.0.0.1:8901/ | grep -q "NeoCorp Cloud Portal" && echo "Room initialized. Discover the services."
