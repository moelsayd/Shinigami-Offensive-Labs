#!/bin/bash
ROOM="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOM"
pkill -f "web_main.py 10010" 2>/dev/null; pkill -f "api_internal.py 10020" 2>/dev/null
pkill -f "ssh_sim.py 10030" 2>/dev/null; pkill -f "ws_server.py 10040" 2>/dev/null
sleep 1
python3 web_main.py 10010 & echo $! > .web.pid
python3 api_internal.py 10020 & echo $! > .api.pid
python3 ssh_sim.py 10030 & echo $! > .ssh.pid
python3 ws_server.py 10040 & echo $! > .ws.pid
sleep 2
curl -s http://127.0.0.1:10010/ | grep -q "ShadowApp" && echo "Room initialized. Discover the services."
