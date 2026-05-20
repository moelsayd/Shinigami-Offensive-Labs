#!/bin/bash
ROOM="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOM"
pkill -f "python3 web_server.py 9101" 2>/dev/null
pkill -f "python3 deser_server.py 9102" 2>/dev/null
pkill -f "python3 ssh_sim.py 9103" 2>/dev/null
sleep 1
python3 web_server.py 9101 & echo $! > .web.pid
python3 deser_server.py 9102 & echo $! > .deser.pid
python3 ssh_sim.py 9103 & echo $! > .ssh.pid
sleep 2
curl -s http://127.0.0.1:9101/ | grep -q "SecureCorp Portal" && echo "Room initialized. Discover the services."
