#!/bin/bash
FLAG_FILE="$(dirname "$(realpath "$0")")/final_flag.txt"
REAL_FLAG=$(cat "$FLAG_FILE")
SCORE="$HOME/ctf-labs/progress.txt"
ROOM_NAME="room75_blackbox_reality"
echo "🏁 Submit the complete flag"
read -p "Flag: " user_flag
if [ "$user_flag" == "$REAL_FLAG" ]; then
    echo "✅ Correct! +15000 points"
    grep -q "$ROOM_NAME" "$SCORE" && sed -i "s/$ROOM_NAME:.*/$ROOM_NAME:15000/g" "$SCORE" || echo "$ROOM_NAME:15000" >> "$SCORE"
    echo "♾️ You have conquered the blackbox reality. You are a true master of inference."
else
    echo "❌ Incorrect flag."
fi
