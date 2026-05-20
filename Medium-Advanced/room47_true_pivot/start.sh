#!/usr/bin/env bash
ROOM="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOM"
pkill -f "python3 web_jwt.py 8101" 2>/dev/null
pkill -f "python3 ssh_sim.py 8103" 2>/dev/null
sleep 1
python3 web_jwt.py 8101 & echo $! > .web.pid
python3 ssh_sim.py 8103 & echo $! > .ssh.pid
sleep 2
if curl -s --connect-timeout 2 http://127.0.0.1:8101/ | grep -q "Employee Portal"; then
    echo "Room initialized. Discover the services."
else
    echo "Room start failed."
fi
