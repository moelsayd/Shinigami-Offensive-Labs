#!/bin/bash
FLAG_FILE="$(dirname "$(realpath "$0")")/flag_final.txt"
REAL_FLAG=$(cat "$FLAG_FILE")
SCORE="$HOME/ctf-labs/progress.txt"
ROOM_NAME="room74_android_enterprise"
echo "🏁 Submit the complete flag"
read -p "Flag: " user_flag
if [ "$user_flag" == "$REAL_FLAG" ]; then
    echo "✅ Correct! +10000 points"
    grep -q "$ROOM_NAME" "$SCORE" && sed -i "s/$ROOM_NAME:.*/$ROOM_NAME:10000/g" "$SCORE" || echo "$ROOM_NAME:10000" >> "$SCORE"
    echo "🔥 Android enterprise fully compromised! You are a mobile security master."
else
    echo "❌ Incorrect flag."
fi
