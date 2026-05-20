#!/bin/bash
FLAG_FILE="$(dirname "$(realpath "$0")")/flag.txt"
REAL_FLAG=$(cat "$FLAG_FILE")
SCORE="$HOME/ctf-labs/progress.txt"
ROOM_NAME="room67_microservice_confusion"
echo "🏁 Submit your flag"
read -p "Flag: " user_flag
if [ "$user_flag" == "$REAL_FLAG" ]; then
    echo "✅ Correct! +5500 points"
    grep -q "$ROOM_NAME" "$SCORE" && sed -i "s/$ROOM_NAME:.*/$ROOM_NAME:5500/g" "$SCORE" || echo "$ROOM_NAME:5500" >> "$SCORE"
    echo "🔥 Microservice identity confusion exploited!"
else
    echo "❌ Incorrect flag."
fi
