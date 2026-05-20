#!/usr/bin/env bash
ROOM="$(cd "$(dirname "$0")" && pwd)"
[ -f "$ROOM/.server.pid" ] && kill $(cat "$ROOM/.server.pid") 2>/dev/null
pkill -f "python3 race_server.py 6085" 2>/dev/null
rm -f "$ROOM/.server.pid"
echo "Server stopped."
