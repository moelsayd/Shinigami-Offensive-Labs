#!/bin/bash
ROOM="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOM"
pkill -f "web_main.py 10201" 2>/dev/null; pkill -f "internal_api.py 10202" 2>/dev/null; pkill -f "ssh_sim.py 10203" 2>/dev/null
sleep 1
python3 web_main.py 10201 & echo $! > .web.pid
python3 internal_api.py 10202 & echo $! > .api.pid
python3 ssh_sim.py 10203 & echo $! > .ssh.pid
sleep 2
curl -s http://127.0.0.1:10201/ | grep -q "MicroCorp" && echo "Room initialized. Discover the services."
