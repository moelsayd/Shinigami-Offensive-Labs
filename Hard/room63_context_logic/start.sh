#!/bin/bash
ROOM="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOM"
pkill -f "web_context.py 9801" 2>/dev/null; pkill -f "yaml_server.py 9802" 2>/dev/null; pkill -f "ssh_sim.py 9803" 2>/dev/null
sleep 1
python3 web_context.py 9801 & echo $! > .web.pid
python3 yaml_server.py 9802 & echo $! > .yaml.pid
python3 ssh_sim.py 9803 & echo $! > .ssh.pid
sleep 2
curl -s http://127.0.0.1:9801/ | grep -q "ContextCorp" && echo "Room initialized. Discover the services."
