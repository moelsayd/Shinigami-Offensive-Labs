#!/bin/bash
FLAG_FILE="$(dirname "$(realpath "$0")")/flag_final.txt"
REAL_FLAG=$(cat "$FLAG_FILE")
SCORE="$HOME/ctf-labs/progress.txt"
ROOM_NAME="room73_final_exam"
echo "🏁 Submit the full flag"
read -p "Flag: " user_flag
if [ "$user_flag" == "$REAL_FLAG" ]; then
    echo "✅ Correct! +9999 points"
    grep -q "$ROOM_NAME" "$SCORE" && sed -i "s/$ROOM_NAME:.*/$ROOM_NAME:9999/g" "$SCORE" || echo "$ROOM_NAME:9999" >> "$SCORE"
    echo "🔥 EclipseCorp fully compromised! You are a master pentester."
else
    echo "❌ Incorrect flag."
fi
