#!/usr/bin/env bash
ROOM="$(cd "$(dirname "$0")" && pwd)"
[ -f "$ROOM/.web.pid" ] && kill $(cat "$ROOM/.web.pid") 2>/dev/null
[ -f "$ROOM/.api.pid" ] && kill $(cat "$ROOM/.api.pid") 2>/dev/null
pkill -f "web_server.py 8501" 2>/dev/null
pkill -f "admin_api.py 8502" 2>/dev/null
rm -f "$ROOM/.web.pid" "$ROOM/.api.pid"
echo "Room stopped."
