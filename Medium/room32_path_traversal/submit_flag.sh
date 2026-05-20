#!/usr/bin/env bash
FLAG_FILE="$(dirname "$(realpath "$0")")/flag.txt"
REAL_FLAG=$(cat "$FLAG_FILE")
SCORE="$HOME/ctf-labs/progress.txt"
ROOM_NAME="room32_path_traversal"

echo "🏁 Submit your flag (format: THM{...})"
read -p "Flag: " user_flag
if [ "$user_flag" == "$REAL_FLAG" ]; then
    echo "✅ Correct! +350 points"
    if grep -q "$ROOM_NAME" "$SCORE"; then
        sed -i "s/$ROOM_NAME:.*/$ROOM_NAME:350/g" "$SCORE"
    else
        echo "$ROOM_NAME:350" >> "$SCORE"
    fi
    echo "🧬 Path traversal mastered!"
else
    echo "❌ Incorrect flag, try again."
fi
