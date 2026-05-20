#!/usr/bin/env bash
ROOM="$(cd "$(dirname "$0")" && pwd)"
if [ -f "$ROOM/.server.pid" ]; then
    kill $(cat "$ROOM/.server.pid") 2>/dev/null
fi
pkill -f "python3 web_server.py 7081" 2>/dev/null
rm -f "$ROOM/.server.pid"
echo "Room stopped."
