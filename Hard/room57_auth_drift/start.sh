#!/bin/bash
ROOM="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOM"
pkill -f "web_oauth.py 9201" 2>/dev/null; pkill -f "oauth_server.py 9202" 2>/dev/null; pkill -f "ws_server.py 9203" 2>/dev/null
sleep 1
python3 web_oauth.py 9201 & echo $! > .web.pid
python3 oauth_server.py 9202 & echo $! > .oauth.pid
python3 ws_server.py 9203 & echo $! > .ws.pid
sleep 2
curl -s http://127.0.0.1:9201/ | grep -q "AuthDrift" && echo "Room initialized. Discover the services."
