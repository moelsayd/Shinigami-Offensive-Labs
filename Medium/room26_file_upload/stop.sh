#!/usr/bin/env bash
ROOM_DIR="$(cd "$(dirname "$0")" && pwd)"
[ -f "$ROOM_DIR/.server.pid" ] && kill $(cat "$ROOM_DIR/.server.pid") 2>/dev/null
pkill -f "python3 file_server.py 6068" 2>/dev/null
rm -f "$ROOM_DIR/.server.pid"
echo "Server stopped."
