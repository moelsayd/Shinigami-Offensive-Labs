#!/usr/bin/env bash
ROOM="$(cd "$(dirname "$0")" && pwd)"
[ -f "$ROOM/.web.pid" ] && kill $(cat "$ROOM/.web.pid") 2>/dev/null
[ -f "$ROOM/.storage.pid" ] && kill $(cat "$ROOM/.storage.pid") 2>/dev/null
pkill -f "python3 web_server.py 7084" 2>/dev/null
pkill -f "python3 storage_server.py 7085" 2>/dev/null
rm -f "$ROOM/.web.pid" "$ROOM/.storage.pid"
echo "Room stopped."
