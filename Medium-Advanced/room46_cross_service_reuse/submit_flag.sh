#!/bin/bash
FLAG_FILE="$(dirname "$(realpath "$0")")/flag.txt"
REAL_FLAG=$(cat "$FLAG_FILE")
SCORE="$HOME/ctf-labs/progress.txt"
ROOM_NAME="room46_cross_service_reuse"
echo "🏁 Submit your flag"
read -p "Flag: " user_flag
if [ "$user_flag" == "$REAL_FLAG" ]; then
    echo "✅ Correct! +800 points"
    grep -q "$ROOM_NAME" "$SCORE" && sed -i "s/$ROOM_NAME:.*/$ROOM_NAME:800/g" "$SCORE" || echo "$ROOM_NAME:800" >> "$SCORE"
    echo "🔑 Cross-service pivot mastered!"
else
    echo "❌ Incorrect flag."
fi
