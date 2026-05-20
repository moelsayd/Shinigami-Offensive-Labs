#!/bin/bash
ROOM="$(cd "$(dirname "$0")" && pwd)"
[ -f "$ROOM/.web.pid" ] && kill $(cat "$ROOM/.web.pid") 2>/dev/null
[ -f "$ROOM/.oauth.pid" ] && kill $(cat "$ROOM/.oauth.pid") 2>/dev/null
[ -f "$ROOM/.ws.pid" ] && kill $(cat "$ROOM/.ws.pid") 2>/dev/null
pkill -f "web_oauth.py 9201" 2>/dev/null; pkill -f "oauth_server.py 9202" 2>/dev/null; pkill -f "ws_server.py 9203" 2>/dev/null
rm -f "$ROOM/.web.pid" "$ROOM/.oauth.pid" "$ROOM/.ws.pid"
echo "Room stopped."
