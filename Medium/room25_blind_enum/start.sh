#!/usr/bin/env bash
ROOM_DIR="$(cd "$(dirname "$0")" && pwd)"
PID_FILE="$ROOM_DIR/.server.pid"
LOG_FILE="$ROOM_DIR/server.log"
PORT=6067

pkill -f "python3 blind_server.py $PORT" 2>/dev/null
sleep 1

cd "$ROOM_DIR"
python3 blind_server.py $PORT > "$LOG_FILE" 2>&1 &
NEW_PID=$!
echo $NEW_PID > "$PID_FILE"

# Wait until server responds
for i in {1..10}; do
    if curl -s --connect-timeout 2 "http://127.0.0.1:$PORT/user?id=1" | grep -q "User Found"; then
        echo "✅ Blind server is running on http://localhost:$PORT"
        echo "🕵️ Enumerate /user?id=... and analyze the responses."
        exit 0
    fi
    sleep 1
done

echo "❌ Failed to start server. Log:"
cat "$LOG_FILE"
kill $NEW_PID 2>/dev/null
rm -f "$PID_FILE"
exit 1
