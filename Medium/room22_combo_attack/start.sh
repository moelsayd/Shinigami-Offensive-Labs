#!/usr/bin/env bash
ROOM_DIR="$(cd "$(dirname "$0")" && pwd)"
PID_FILE="$ROOM_DIR/.server.pid"
LOG_FILE="$ROOM_DIR/server.log"
PORT=6063

# Kill any old instance
pkill -f "python3 combo_server.py $PORT" 2>/dev/null
sleep 1

cd "$ROOM_DIR"
python3 combo_server.py $PORT > "$LOG_FILE" 2>&1 &
NEW_PID=$!
echo $NEW_PID > "$PID_FILE"

# Wait until server responds
for i in {1..10}; do
    if curl -s -o /dev/null --connect-timeout 2 "http://127.0.0.1:$PORT/" ; then
        echo "✅ Combo server is running on http://localhost:$PORT"
        echo "📂 Use directory brute-forcing + parameter fuzzing."
        exit 0
    fi
    sleep 1
done

echo "❌ Failed to start server. Log:"
cat "$LOG_FILE"
kill $NEW_PID 2>/dev/null
rm -f "$PID_FILE"
exit 1
