#!/usr/bin/env bash
ROOM_DIR="$(cd "$(dirname "$0")" && pwd)"
[ -f "$ROOM_DIR/.server.pid" ] && kill $(cat "$ROOM_DIR/.server.pid") 2>/dev/null
pkill -f "python3 api_server.py 6069" 2>/dev/null
rm -f "$ROOM_DIR/.server.pid"
echo "Server stopped."
