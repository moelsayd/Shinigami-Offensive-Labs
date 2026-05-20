#!/bin/bash
ROOM_DIR="$(cd "$(dirname "$0")" && pwd)"
PID_FILE="$ROOM_DIR/.server.pid"
echo "🛑 Stopping service..."
[ -f "$PID_FILE" ] && kill $(cat "$PID_FILE") 2>/dev/null
pkill -f "python3 service_server.py 9001" 2>/dev/null
rm -f "$PID_FILE"
echo "✅ Done."
