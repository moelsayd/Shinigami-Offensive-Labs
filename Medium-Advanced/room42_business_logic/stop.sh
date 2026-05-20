#!/usr/bin/env bash
ROOM="$(cd "$(dirname "$0")" && pwd)"
[ -f "$ROOM/.main.pid" ] && kill $(cat "$ROOM/.main.pid") 2>/dev/null
[ -f "$ROOM/.dash.pid" ] && kill $(cat "$ROOM/.dash.pid") 2>/dev/null
pkill -f "main_server.py 7101" 2>/dev/null
pkill -f "dashboard_server.py 7102" 2>/dev/null
rm -f "$ROOM/.main.pid" "$ROOM/.dash.pid"
echo "Room stopped."
