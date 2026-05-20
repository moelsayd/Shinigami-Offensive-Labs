#!/usr/bin/env bash
ROOM_DIR="$(cd "$(dirname "$0")" && pwd)"
PID_FILE="$ROOM_DIR/.server.pid"
LOG_FILE="$ROOM_DIR/server.log"
PORT=6065

# Kill any old instance
pkill -f "python3 mass_server.py $PORT" 2>/dev/null
sleep 1

cd "$ROOM_DIR"
python3 mass_server.py $PORT > "$LOG_FILE" 2>&1 &
NEW_PID=$!
echo $NEW_PID > "$PID_FILE"

# Wait until server responds
for i in {1..10}; do
    if curl -s --connect-timeout 2 -X POST -H "Content-Type: application/json" \
        -d '{"user":"ping"}' "http://127.0.0.1:$PORT/register" > /dev/null 2>&1; then
        echo "✅ Mass Assignment server is running on http://localhost:$PORT"
        echo "📡 Challenge: find the /register endpoint and tamper with JSON fields."
        exit 0
    fi
    sleep 1
done

echo "❌ Failed to start server. Log:"
cat "$LOG_FILE"
kill $NEW_PID 2>/dev/null
rm -f "$PID_FILE"
exit 1
