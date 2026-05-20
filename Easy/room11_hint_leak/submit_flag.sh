#!/bin/bash
FLAG_FILE="$(dirname "$(realpath "$0")")/flag.txt"
REAL_FLAG=$(cat "$FLAG_FILE")
SCORE_FILE="$HOME/ctf-labs/progress.txt"
ROOM_NAME="room11_hint_leak"

echo "🏁 Submit your flag (format: THM{...})"
read -p "Flag: " user_flag

if [ "$user_flag" == "$REAL_FLAG" ]; then
    echo "✅ Correct! +150 points"
    if grep -q "$ROOM_NAME" "$SCORE_FILE"; then
        sed -i "s/$ROOM_NAME:.*/$ROOM_NAME:150/g" "$SCORE_FILE"
    else
        echo "$ROOM_NAME:150" >> "$SCORE_FILE"
    fi
    echo "📝 Chained information leakage leads to full compromise."
else
    echo "❌ Incorrect flag, try again."
fi
