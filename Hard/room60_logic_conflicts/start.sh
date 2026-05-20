#!/bin/bash
ROOM="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOM"
pkill -f "web_logic.py 9501" 2>/dev/null; pkill -f "xxe_server.py 9502" 2>/dev/null; pkill -f "ssh_sim.py 9503" 2>/dev/null
sleep 1
python3 web_logic.py 9501 & echo $! > .web.pid
python3 xxe_server.py 9502 & echo $! > .xxe.pid
python3 ssh_sim.py 9503 & echo $! > .ssh.pid
sleep 2
curl -s http://127.0.0.1:9501/ | grep -q "BizLogic Corp" && echo "Room initialized. Discover the services."
