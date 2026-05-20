#!/bin/bash
FLAG_FILE="$(dirname "$(realpath "$0")")/flag.txt"
REAL_FLAG=$(cat "$FLAG_FILE")
SCORE="$HOME/ctf-labs/progress.txt"
ROOM_NAME="room59_ghost_endpoints"
echo "🏁 Submit your flag"
read -p "Flag: " user_flag
if [ "$user_flag" == "$REAL_FLAG" ]; then
    echo "✅ Correct! +4000 points"
    grep -q "$ROOM_NAME" "$SCORE" && sed -i "s/$ROOM_NAME:.*/$ROOM_NAME:4000/g" "$SCORE" || echo "$ROOM_NAME:4000" >> "$SCORE"
    echo "👻 Ghost endpoints + cache poison mastered!"
else
    echo "❌ Incorrect flag."
fi
