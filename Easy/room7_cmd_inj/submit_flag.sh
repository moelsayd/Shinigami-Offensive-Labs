#!/bin/bash
FLAG_FILE="$(dirname "$(realpath "$0")")/flag.txt"
REAL_FLAG=$(cat "$FLAG_FILE")
SCORE_FILE="$HOME/ctf-labs/progress.txt"
ROOM_NAME="room7_cmd_inj"

echo "🏁 Submit your flag (format: THM{...})"
read -p "Flag: " user_flag

if [ "$user_flag" == "$REAL_FLAG" ]; then
    echo "✅ Correct! +200 points"
    if grep -q "$ROOM_NAME" "$SCORE_FILE"; then
        sed -i "s/$ROOM_NAME:.*/$ROOM_NAME:200/g" "$SCORE_FILE"
    else
        echo "$ROOM_NAME:200" >> "$SCORE_FILE"
    fi
    echo "🔥 Command injection mastered!"
else
    echo "❌ Incorrect flag, try again."
fi
