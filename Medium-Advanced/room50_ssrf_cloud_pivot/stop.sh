#!/usr/bin/env bash
ROOM="$(cd "$(dirname "$0")" && pwd)"
[ -f "$ROOM/.web.pid" ] && kill $(cat "$ROOM/.web.pid") 2>/dev/null
[ -f "$ROOM/.meta.pid" ] && kill $(cat "$ROOM/.meta.pid") 2>/dev/null
[ -f "$ROOM/.admin.pid" ] && kill $(cat "$ROOM/.admin.pid") 2>/dev/null
pkill -f "web_server.py 8401" 2>/dev/null
pkill -f "metadata_server.py 8402" 2>/dev/null
pkill -f "admin_api.py 8403" 2>/dev/null
rm -f "$ROOM/.web.pid" "$ROOM/.meta.pid" "$ROOM/.admin.pid"
echo "Room stopped."
