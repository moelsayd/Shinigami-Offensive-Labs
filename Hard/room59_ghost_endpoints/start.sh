#!/bin/bash
ROOM="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOM"
pkill -f "web_ghost.py 9401" 2>/dev/null; pkill -f "cache_server.py 9402" 2>/dev/null; pkill -f "ssh_sim.py 9403" 2>/dev/null
sleep 1
python3 web_ghost.py 9401 & echo $! > .web.pid
python3 cache_server.py 9402 & echo $! > .cache.pid
python3 ssh_sim.py 9403 & echo $! > .ssh.pid
sleep 2
curl -s http://127.0.0.1:9401/ | grep -q "GhostCorp Portal" && echo "Room initialized. Discover the services."
