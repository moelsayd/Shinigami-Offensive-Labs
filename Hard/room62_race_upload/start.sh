#!/bin/bash
ROOM="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOM"
pkill -f "web_race.py 9701" 2>/dev/null; pkill -f "ssh_sim.py 9702" 2>/dev/null
sleep 1
python3 web_race.py 9701 & echo $! > .web.pid
python3 ssh_sim.py 9702 & echo $! > .ssh.pid
sleep 2
curl -s http://127.0.0.1:9701/ | grep -q "FileVault" && echo "Room initialized. Discover the services."
