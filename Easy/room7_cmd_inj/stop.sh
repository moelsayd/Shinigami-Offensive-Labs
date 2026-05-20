#!/bin/bash
ROOM_DIR="$(cd "$(dirname "$0")" && pwd)"
PID_FILE="$ROOM_DIR/.server.pid"
echo "🛑 Stopping vulnerable server..."
[ -f "$PID_FILE" ] && kill $(cat "$PID_FILE") 2>/dev/null
pkill -f "python3 vulnerable_server.py 7777" 2>/dev/null
rm -f "$PID_FILE"
echo "✅ Done."
