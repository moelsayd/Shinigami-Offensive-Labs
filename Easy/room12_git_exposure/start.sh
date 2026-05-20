#!/bin/bash
ROOM_DIR="$(cd "$(dirname "$0")" && pwd)"
TARGET_DIR="$ROOM_DIR/target"
PID_FILE="$ROOM_DIR/.server.pid"
PORT=6060
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

# Check that server responds and .git directory is accessible
if curl -s --connect-timeout 3 "$URL" | grep -q "Welcome"; then
    if curl -s --connect-timeout 3 "$URL/.git/config" | grep -q "repositoryformatversion"; then
        echo "✅ Server is running at $URL"
        echo "📁 .git directory is exposed – enumerate it."
    else
        echo "❌ Server is running but .git directory not found. Check target folder."
        kill $NEW_PID 2>/dev/null
        rm -f "$PID_FILE"
        exit 1
    fi
else
    echo "❌ Failed to start the server on port $PORT."
    kill $NEW_PID 2>/dev/null
    rm -f "$PID_FILE"
    exit 1
fi
