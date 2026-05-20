#!/bin/bash
FLAG_FILE="$(dirname "$(realpath "$0")")/flag.txt"
REAL_FLAG=$(cat "$FLAG_FILE")
SCORE="$HOME/ctf-labs/progress.txt"
ROOM_NAME="room56_hard_partial_exposure"
echo "🏁 Submit your flag"
read -p "Flag: " user_flag
if [ "$user_flag" == "$REAL_FLAG" ]; then
    echo "✅ Correct! +3000 points"
    grep -q "$ROOM_NAME" "$SCORE" && sed -i "s/$ROOM_NAME:.*/$ROOM_NAME:3000/g" "$SCORE" || echo "$ROOM_NAME:3000" >> "$SCORE"
    echo "🔥 Hard level initiated! Incomplete context exploited."
else
    echo "❌ Incorrect flag."
fi
