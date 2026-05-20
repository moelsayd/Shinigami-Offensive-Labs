#!/bin/bash
ROOM_DIR="$(cd "$(dirname "$0")" && pwd)"
PID_FILE="$ROOM_DIR/.server.pid"
LOG_FILE="$ROOM_DIR/server.log"
PORT=5555

# Kill any old instance
pkill -f "python3 adb_simulator.py $PORT" 2>/dev/null
sleep 1

cd "$ROOM_DIR"
python3 adb_simulator.py $PORT > "$LOG_FILE" 2>&1 &
NEW_PID=$!
echo $NEW_PID > "$PID_FILE"

# Wait until port is open
for i in {1..10}; do
    if nc -z 127.0.0.1 $PORT 2>/dev/null; then
        echo "✅ ADB simulator is running on 127.0.0.1:$PORT"
        echo "🔌 Connect with: nc 127.0.0.1 $PORT"
        exit 0
    fi
    sleep 1
done

echo "❌ Failed to start ADB simulator. Check $LOG_FILE:"
cat "$LOG_FILE"
kill $NEW_PID 2>/dev/null
rm -f "$PID_FILE"
exit 1
