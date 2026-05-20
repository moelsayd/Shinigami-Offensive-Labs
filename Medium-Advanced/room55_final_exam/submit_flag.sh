#!/bin/bash
FLAG_FILE="$(dirname "$(realpath "$0")")/flag.txt"
REAL_FLAG=$(cat "$FLAG_FILE")
SCORE="$HOME/ctf-labs/progress.txt"
ROOM_NAME="room55_final_exam"
echo "🏁 Submit your flag"
read -p "Flag: " user_flag
if [ "$user_flag" == "$REAL_FLAG" ]; then
    echo "✅ Correct! +2500 points"
    grep -q "$ROOM_NAME" "$SCORE" && sed -i "s/$ROOM_NAME:.*/$ROOM_NAME:2500/g" "$SCORE" || echo "$ROOM_NAME:2500" >> "$SCORE"
    echo "🏆 Medium-Advanced certification complete! You are now a true pentester."
else
    echo "❌ Incorrect flag."
fi
