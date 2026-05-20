#!/usr/bin/env bash
FLAG_FILE="$(dirname "$(realpath "$0")")/flag.txt"
REAL_FLAG=$(cat "$FLAG_FILE")
SCORE="$HOME/ctf-labs/progress.txt"
ROOM_NAME="room53_adb_api_bypass"
echo "🏁 Submit your flag"
read -p "Flag: " user_flag
if [ "$user_flag" == "$REAL_FLAG" ]; then
    echo "✅ Correct! +1200 points"
    grep -q "$ROOM_NAME" "$SCORE" && sed -i "s/$ROOM_NAME:.*/$ROOM_NAME:1200/g" "$SCORE" || echo "$ROOM_NAME:1200" >> "$SCORE"
    echo "📱 ADB + Burp + Auth Bypass chain complete! You are a mobile pentester."
else
    echo "❌ Incorrect flag."
fi
