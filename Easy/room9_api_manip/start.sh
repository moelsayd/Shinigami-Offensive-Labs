#!/bin/bash
ROOM_DIR="$(cd "$(dirname "$0")" && pwd)"
PID_FILE="$ROOM_DIR/.server.pid"
PORT=9090

# Kill any old instance
pkill -f "python3 api_server.py $PORT" 2>/dev/null
sleep 1

cd "$ROOM_DIR"
python3 api_server.py $PORT &>/dev/null &
NEW_PID=$!
echo $NEW_PID > "$PID_FILE"
sleep 2

# Check if server is responding to the API
if curl -s --connect-timeout 3 "http://localhost:$PORT/user?id=admin" | grep -q "Welcome"; then
    echo "✅ API server is running at http://localhost:$PORT"
    echo "🔍 Explore the /user endpoint with different id parameters."
else
    echo "❌ Failed to start the API server."
    kill $NEW_PID 2>/dev/null
    rm -f "$PID_FILE"
    exit 1
fi
