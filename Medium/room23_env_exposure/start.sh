#!/usr/bin/env bash
ROOM_DIR="$(cd "$(dirname "$0")" && pwd)"
TARGET_DIR="$ROOM_DIR/target"
PID_FILE="$ROOM_DIR/.server.pid"
PORT=6064
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

# Double‑check: server responds AND .env is accessible
if curl -s --connect-timeout 3 "$URL" | grep -q "Secure Portal"; then
    if curl -s --connect-timeout 3 --output /dev/null --head --fail "$URL/.env"; then
        echo "✅ Server is running at $URL"
        echo "🕵️ Think about files developers may have left exposed."
    else
        echo "⚠️  Server is running but .env file may not be accessible (check permissions)."
    fi
else
    echo "❌ Failed to start server on port $PORT."
    kill $NEW_PID 2>/dev/null
    rm -f "$PID_FILE"
    exit 1
fi
