#!/bin/bash
ROOM="$(cd "$(dirname "$0")" && pwd)"
[ -f "$ROOM/.web.pid" ] && kill $(cat "$ROOM/.web.pid") 2>/dev/null
[ -f "$ROOM/.graphql.pid" ] && kill $(cat "$ROOM/.graphql.pid") 2>/dev/null
pkill -f "web_server.py 9301" 2>/dev/null; pkill -f "graphql_server.py 9302" 2>/dev/null
rm -f "$ROOM/.web.pid" "$ROOM/.graphql.pid"
echo "Room stopped."
