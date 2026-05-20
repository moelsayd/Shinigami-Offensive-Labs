#!/bin/bash
ROOM="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOM"
pkill -f "web_main.py 10901" 2>/dev/null; pkill -f "monitor_api.py 10922" 2>/dev/null; pkill -f "transaction_worker.py 10933" 2>/dev/null; pkill -f "ssh_sim.py 10944" 2>/dev/null
sleep 1
python3 web_main.py 10901 & echo $! > .web.pid
python3 monitor_api.py 10922 & echo $! > .mon.pid
python3 transaction_worker.py 10933 & echo $! > .work.pid
python3 ssh_sim.py 10944 & echo $! > .ssh.pid
sleep 2
curl -s http://127.0.0.1:10901/ | grep -q "FinCorp" && echo "Room initialized. Discover the services."
