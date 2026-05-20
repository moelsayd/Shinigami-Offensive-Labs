#!/bin/bash
ROOM_DIR="$(cd "$(dirname "$0")" && pwd)"
PID_FILE="$ROOM_DIR/.server.pid"
LOG_FILE="$ROOM_DIR/server.log"
PORT=2222

# قتل أي نسخة سابقة
pkill -f "python3 ssh_simulator.py $PORT" 2>/dev/null
sleep 1

cd "$ROOM_DIR"

# تشغيل الخادم وتسجيل كل شيء في log
python3 ssh_simulator.py $PORT > "$LOG_FILE" 2>&1 &
NEW_PID=$!
echo $NEW_PID > "$PID_FILE"

# انتظر حتى يكتب "READY" في السجل (مؤشر نجاح)
for i in {1..10}; do
    if grep -q "READY $PORT" "$LOG_FILE" 2>/dev/null; then
        echo "✅ SSH simulator is running on 127.0.0.1:$PORT"
        echo "🔑 Connect with: nc 127.0.0.1 $PORT"
        exit 0
    fi
    sleep 1
done

# إذا وصلنا هنا، لم تظهر الرسالة -> فشل
echo "❌ Failed to start SSH simulator. Check $LOG_FILE:"
cat "$LOG_FILE"
kill $NEW_PID 2>/dev/null
rm -f "$PID_FILE"
exit 1
