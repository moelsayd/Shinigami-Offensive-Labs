#!/usr/bin/env bash
ROOM="$(cd "$(dirname "$0")" && pwd)"
[ -f "$ROOM/.api.pid" ] && kill $(cat "$ROOM/.api.pid") 2>/dev/null
[ -f "$ROOM/.adb.pid" ] && kill $(cat "$ROOM/.adb.pid") 2>/dev/null
pkill -f "api_server.py 8701" 2>/dev/null
pkill -f "adb_sim.py 8702" 2>/dev/null
rm -f "$ROOM/.api.pid" "$ROOM/.adb.pid"
echo "Room stopped."
