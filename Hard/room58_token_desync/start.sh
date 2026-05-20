#!/bin/bash
ROOM="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOM"
pkill -f "python3 web_server.py 9301" 2>/dev/null
pkill -f "python3 graphql_server.py 9302" 2>/dev/null
sleep 1
python3 web_server.py 9301 & echo $! > .web.pid
python3 graphql_server.py 9302 & echo $! > .graphql.pid
sleep 2
curl -s http://127.0.0.1:9301/ | grep -q "Desync Corp" && echo "Room initialized. Discover the services."
