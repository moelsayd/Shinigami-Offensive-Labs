#!/bin/bash
ROOM_DIR="$(cd "$(dirname "$0")" && pwd)"
TARGET_DIR="$ROOM_DIR/target"
PID_FILE="$ROOM_DIR/.server.pid"
PORT=6061
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

# Check that server responds and at least one backup file is accessible
if curl -s --connect-timeout 3 "$URL/index.php" | grep -q "live site"; then
    if curl -s --connect-timeout 3 --output /dev/null --head --fail "$URL/config.php.save"; then
        echo "✅ Server is running at $URL"
        echo "🔍 Backup files exist – use extension fuzzing to find them."
    else
        echo "⚠️  Server running but backup files not detected (check file permissions)."
    fi
else
    echo "❌ Failed to start server on port $PORT."
    kill $NEW_PID 2>/dev/null
    rm -f "$PID_FILE"
    exit 1
fi
