#!/bin/bash
ROOM="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOM"
pkill -f "python3 web_server.py 7501" 2>/dev/null
pkill -f "python3 ssh_server.py 7502" 2>/dev/null
pkill -f "python3 db_server.py 7503" 2>/dev/null
sleep 1
python3 web_server.py 7501 & echo $! > .web.pid
python3 ssh_server.py 7502 & echo $! > .ssh.pid
python3 db_server.py 7503 & echo $! > .db.pid
sleep 2
if curl -s --connect-timeout 2 http://127.0.0.1:7501/ | grep -q "Employee Portal"; then
    echo "Room initialized. Discover the services."
else
    echo "Room start failed."
fi
