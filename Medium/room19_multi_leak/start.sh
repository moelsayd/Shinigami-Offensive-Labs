#!/bin/bash
ROOM_DIR="$(cd "$(dirname "$0")" && pwd)"
TARGET_DIR="$ROOM_DIR/target"
PID_FILE="$ROOM_DIR/.server.pid"
PORT=7070
URL="http://localhost:$PORT"

if [ ! -d "$TARGET_DIR" ]; then
    echo "❌ target directory missing!"
    exit 1
fi

# Kill any old server on this port
pkill -f "python3 -m http.server $PORT" 2>/dev/null
sleep 1

cd "$TARGET_DIR"
python3 -m http.server $PORT --bind 127.0.0.1 &>/dev/null &
NEW_PID=$!
echo $NEW_PID > "$PID_FILE"
sleep 2

# Check server responds and robots.txt is accessible
if curl -s --connect-timeout 3 "$URL/robots.txt" | grep -q "Disallow"; then
    echo "✅ Server is running at $URL"
    echo "🔍 Begin your multi-stage recon."
else
    echo "❌ Failed to start server on port $PORT."
    kill $NEW_PID 2>/dev/null
    rm -f "$PID_FILE"
    exit 1
fi
