#!/bin/bash
ROOM_DIR="$(cd "$(dirname "$0")" && pwd)"
PID_FILE="$ROOM_DIR/.server.pid"
LOG_FILE="$ROOM_DIR/server.log"
PORT=7071

pkill -f "python3 js_admin_server.py $PORT" 2>/dev/null
sleep 1

cd "$ROOM_DIR"
python3 js_admin_server.py $PORT > "$LOG_FILE" 2>&1 &
NEW_PID=$!
echo $NEW_PID > "$PID_FILE"

# Wait for server to start
for i in {1..10}; do
    if curl -s -o /dev/null -w "%{http_code}" --connect-timeout 2 "http://127.0.0.1:$PORT/" | grep -q "200"; then
        echo "✅ Server is running on http://localhost:$PORT"
        echo "🔍 Inspect the source and JavaScript files carefully."
        exit 0
    fi
    sleep 1
done

echo "❌ Failed to start server. Check $LOG_FILE:"
cat "$LOG_FILE"
kill $NEW_PID 2>/dev/null
rm -f "$PID_FILE"
exit 1
