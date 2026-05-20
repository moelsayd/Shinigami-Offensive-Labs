#!/bin/bash
ROOM_DIR="$(cd "$(dirname "$0")" && pwd)"
PID_FILE="$ROOM_DIR/.server.pid"
PORT=7777

# إيقاف أي نسخة قديمة
pkill -f "python3 vulnerable_server.py $PORT" 2>/dev/null
sleep 1

cd "$ROOM_DIR"
python3 vulnerable_server.py $PORT &>/dev/null &
NEW_PID=$!
echo $NEW_PID > "$PID_FILE"

# انتظر حتى يصبح الخادم جاهزاً (بحد أقصى 15 ثانية)
for i in {1..15}; do
    if nc -z 127.0.0.1 $PORT 2>/dev/null; then
        echo "✅ Server is running on 127.0.0.1:$PORT"
        echo "💉 Connect with: nc 127.0.0.1 $PORT"
        exit 0
    fi
    sleep 1
done

echo "❌ Failed to start the vulnerable server."
kill $NEW_PID 2>/dev/null
rm -f "$PID_FILE"
exit 1
