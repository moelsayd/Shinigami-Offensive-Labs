#!/usr/bin/env bash
FLAG_FILE="$(dirname "$(realpath "$0")")/flag.txt"
REAL_FLAG=$(cat "$FLAG_FILE")
SCORE="$HOME/ctf-labs/progress.txt"
ROOM_NAME="room50_ssrf_cloud_pivot"
echo "🏁 Submit your flag"
read -p "Flag: " user_flag
if [ "$user_flag" == "$REAL_FLAG" ]; then
    echo "✅ Correct! +1000 points"
    grep -q "$ROOM_NAME" "$SCORE" && sed -i "s/$ROOM_NAME:.*/$ROOM_NAME:1000/g" "$SCORE" || echo "$ROOM_NAME:1000" >> "$SCORE"
    echo "☁️ Internal cloud pivoted via SSRF + NoSQLi!"
else
    echo "❌ Incorrect flag."
fi
