#!/bin/bash
ROOM="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOM"
pkill -f "graphql_main.py 10101" 2>/dev/null; pkill -f "async_worker.py 10102" 2>/dev/null; pkill -f "ssh_sim.py 10103" 2>/dev/null
sleep 1
python3 graphql_main.py 10101 & echo $! > .web.pid
python3 async_worker.py 10102 & echo $! > .worker.pid
python3 ssh_sim.py 10103 & echo $! > .ssh.pid
sleep 2
curl -s http://127.0.0.1:10101/ | grep -q "Ambiguous Corp" && echo "Room initialized. Discover the services."
