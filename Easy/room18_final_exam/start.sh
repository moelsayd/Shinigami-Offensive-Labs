#!/bin/bash
ROOM_DIR="$(cd "$(dirname "$0")" && pwd)"
PID_FILE="$ROOM_DIR/.server.pid"
LOG_FILE="$ROOM_DIR/server.log"
PORT=8888

pkill -f "python3 neocorp_server.py $PORT" 2>/dev/null
sleep 1

cd "$ROOM_DIR"
python3 neocorp_server.py $PORT > "$LOG_FILE" 2>&1 &
NEW_PID=$!
echo $NEW_PID > "$PID_FILE"

for i in {1..10}; do
    if curl -s -o /dev/null -w "%{http_code}" --connect-timeout 2 "http://127.0.0.1:$PORT/" | grep -q "200"; then
        echo "✅ NeoCorp Portal is running on http://localhost:$PORT"
        echo "🔍 Begin your recon – think like a pentester."
        exit 0
    fi
    sleep 1
done

echo "❌ Failed to start server. Check $LOG_FILE:"
cat "$LOG_FILE"
kill $NEW_PID 2>/dev/null
rm -f "$PID_FILE"
exit 1
