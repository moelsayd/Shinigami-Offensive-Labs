#!/bin/bash
ROOM_DIR="$(cd "$(dirname "$0")" && pwd)"
PID_FILE="$ROOM_DIR/.server.pid"
echo "🛑 Stopping ADB simulator..."
[ -f "$PID_FILE" ] && kill $(cat "$PID_FILE") 2>/dev/null
pkill -f "python3 adb_simulator.py 5555" 2>/dev/null
rm -f "$PID_FILE"
echo "✅ Done."
