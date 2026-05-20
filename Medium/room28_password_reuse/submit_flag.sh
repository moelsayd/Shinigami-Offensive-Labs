#!/usr/bin/env bash
FLAG_FILE="$(dirname "$(realpath "$0")")/flag.txt"
REAL_FLAG=$(cat "$FLAG_FILE")
SCORE_FILE="$HOME/ctf-labs/progress.txt"
ROOM_NAME="room28_password_reuse"

echo "🏁 Submit your flag (format: THM{...})"
read -p "Flag: " user_flag
if [ "$user_flag" == "$REAL_FLAG" ]; then
    echo "✅ Correct! +300 points"
    if grep -q "$ROOM_NAME" "$SCORE_FILE"; then
        sed -i "s/$ROOM_NAME:.*/$ROOM_NAME:300/g" "$SCORE_FILE"
    else
        echo "$ROOM_NAME:300" >> "$SCORE_FILE"
    fi
    echo "🔑 Password reuse is the silent killer of enterprise security!"
else
    echo "❌ Incorrect flag, try again."
fi
