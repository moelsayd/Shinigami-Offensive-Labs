#!/bin/bash
ROOM_DIR="$(cd "$(dirname "$0")" && pwd)"
TARGET_DIR="$ROOM_DIR/target"
PID_FILE="$ROOM_DIR/.server.pid"
PORT=8088
URL="http://localhost:${PORT}"
EXPECTED_STRING="Maybe check /secret.html"

if [ ! -d "$TARGET_DIR" ]; then
    echo "❌ target directory missing!"
    exit 1
fi

echo "🔍 Cleaning any previous server on port ${PORT}..."
pkill -f "python3 -m http.server ${PORT}" 2>/dev/null
sleep 1

cd "$TARGET_DIR"
python3 -m http.server ${PORT} --bind 127.0.0.1 &>/dev/null &
NEW_PID=$!
echo ${NEW_PID} > "${PID_FILE}"

# انتظر حتى يصبح الخادم جاهزاً (بحد أقصى 15 ثانية)
for i in {1..15}; do
    if curl -s --connect-timeout 2 "${URL}" 2>/dev/null | grep -q "${EXPECTED_STRING}"; then
        echo "✅ Lab is running at: ${URL}"
        echo "🌐 Use curl or a browser."
        exit 0
    fi
    sleep 1
done

echo "❌ Failed to start lab on port ${PORT}."
echo "Try: pkill -f http.server && fuser -k ${PORT}/tcp"
kill ${NEW_PID} 2>/dev/null
rm -f "${PID_FILE}"
exit 1
