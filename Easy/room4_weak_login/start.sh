#!/bin/bash
ROOM_DIR="$(cd "$(dirname "$0")" && pwd)"
PID_FILE="$ROOM_DIR/.server.pid"
PORT=7000
URL="http://localhost:$PORT"

# Stop any old instance
pkill -f "python3 login_server.py $PORT" 2>/dev/null
sleep 1

cd "$ROOM_DIR"
python3 login_server.py $PORT &>/dev/null &
NEW_PID=$!
echo $NEW_PID > "$PID_FILE"
sleep 2

# Check if the server responds
if curl -s --connect-timeout 3 "$URL" | grep -q "Restricted Area"; then
    echo "✅ Server is running at $URL"
    echo "🔑 Try to guess the login credentials."
else
    echo "❌ Failed to start the login server."
    kill $NEW_PID 2>/dev/null
    rm -f "$PID_FILE"
    exit 1
fi
