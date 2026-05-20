#!/bin/bash
ROOM_DIR="$(cd "$(dirname "$0")" && pwd)"
TARGET_DIR="$ROOM_DIR/target"
PID_FILE="$ROOM_DIR/.server.pid"
PORT=9000
URL="http://localhost:$PORT"

if [ ! -d "$TARGET_DIR" ]; then
    echo "❌ target directory not found!"
    exit 1
fi

# Stop any existing server on the same port
pkill -f "python3 -m http.server $PORT" 2>/dev/null
sleep 1

cd "$TARGET_DIR"
python3 -m http.server $PORT --bind 127.0.0.1 &>/dev/null &
NEW_PID=$!
echo $NEW_PID > "$PID_FILE"
sleep 2

# Verify that the server is running and returns the correct content
if curl -s --connect-timeout 3 "$URL" | grep -q "Welcome"; then
    echo "✅ Server running at: $URL"
    echo "🔍 Use gobuster or dirb to search for hidden directories."
else
    echo "❌ Failed to start server on port $PORT."
    kill $NEW_PID 2>/dev/null
    rm -f "$PID_FILE"
    exit 1
fi
