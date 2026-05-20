#!/bin/bash
FLAG_FILE="$(dirname "$(realpath "$0")")/flag.txt"
REAL_FLAG=$(cat "$FLAG_FILE")
SCORE="$HOME/ctf-labs/progress.txt"
ROOM_NAME="room65_shadow_api"
echo "🏁 Submit your flag"
read -p "Flag: " user_flag
if [ "$user_flag" == "$REAL_FLAG" ]; then
    echo "✅ Correct! +5000 points"
    grep -q "$ROOM_NAME" "$SCORE" && sed -i "s/$ROOM_NAME:.*/$ROOM_NAME:5000/g" "$SCORE" || echo "$ROOM_NAME:5000" >> "$SCORE"
    echo "🔥 Shadow APIs + Prototype Pollution + WebSocket owned!"
else
    echo "❌ Incorrect flag."
fi
