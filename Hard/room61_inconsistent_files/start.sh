#!/bin/bash
ROOM="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOM"
pkill -f "web_server.py 9601" 2>/dev/null; pkill -f "padding_oracle.py 9602" 2>/dev/null; pkill -f "ssh_sim.py 9603" 2>/dev/null
sleep 1
python3 web_server.py 9601 & echo $! > .web.pid
python3 padding_oracle.py 9602 & echo $! > .oracle.pid
python3 ssh_sim.py 9603 & echo $! > .ssh.pid
sleep 2
curl -s http://127.0.0.1:9601/ | grep -q "FileCorp" && echo "Room initialized. Discover the services."
