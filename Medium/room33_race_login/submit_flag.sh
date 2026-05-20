#!/usr/bin/env bash
FLAG_FILE="$(dirname "$(realpath "$0")")/flag.txt"
REAL_FLAG=$(cat "$FLAG_FILE")
SCORE="$HOME/ctf-labs/progress.txt"
ROOM_NAME="room33_race_login"

echo "🏁 Submit your flag (format: THM{...})"
read -p "Flag: " user_flag
if [ "$user_flag" == "$REAL_FLAG" ]; then
    echo "✅ Correct! +400 points"
    if grep -q "$ROOM_NAME" "$SCORE"; then
        sed -i "s/$ROOM_NAME:.*/$ROOM_NAME:400/g" "$SCORE"
    else
        echo "$ROOM_NAME:400" >> "$SCORE"
    fi
    echo "⏱️ Race condition mastered!"
else
    echo "❌ Incorrect flag, try again."
fi
