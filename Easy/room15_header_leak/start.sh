#!/bin/bash
ROOM_DIR="$(cd "$(dirname "$0")" && pwd)"
PID_FILE="$ROOM_DIR/.server.pid"
LOG_FILE="$ROOM_DIR/server.log"
PORT=5050

# Kill any old instance
pkill -f "python3 header_server.py $PORT" 2>/dev/null
sleep 1

cd "$ROOM_DIR"
python3 header_server.py $PORT > "$LOG_FILE" 2>&1 &
NEW_PID=$!
echo $NEW_PID > "$PID_FILE"

# Wait until server responds with a 200 OK
for i in {1..10}; do
    response=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 2 "http://127.0.0.1:$PORT/")
    if [ "$response" = "200" ]; then
        echo "✅ Server is running on http://localhost:$PORT"
        echo "📋 Inspect the response headers (curl -I http://localhost:$PORT)"
        exit 0
    fi
    sleep 1
done

echo "❌ Startup check failed (HTTP code: $response). Check $LOG_FILE:"
cat "$LOG_FILE"
kill $NEW_PID 2>/dev/null
rm -f "$PID_FILE"
exit 1
