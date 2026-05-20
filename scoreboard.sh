#!/bin/bash

CYAN='\e[1;36m'
YELLOW='\e[1;33m'
GREEN='\e[1;32m'
RESET='\e[0m'

#PURPLE='\e[38;5;141m'
PURPLE='\e[38;5;93m'



BASE="$HOME/ctf-labs"
PROGRESS="$BASE/progress.txt"

echo -e "${PURPLE}======================================"
echo -e "🏆 Shinigami CTF Scoreboard"
echo -e "======================================${RESET}"
echo ""

if [ ! -f "$PROGRESS" ]; then
    echo -e "${YELLOW}No progress recorded yet.${RESET}"
    exit 0
fi

for level in Easy Medium Medium-Advanced Hard; do
    level_dir="$BASE/$level"

    if [ -d "$level_dir" ]; then
        echo -e "${CYAN}[ $level ]${RESET}"

        level_total=0

        for room in "$level_dir"/room*; do
            [ -d "$room" ] || continue

            room_name=$(basename "$room")
            pts=$(grep "^${room_name}:" "$PROGRESS" 2>/dev/null | cut -d: -f2)

            if [ -n "$pts" ]; then
                echo -e "  ${GREEN}$room_name${RESET} : $pts"
                level_total=$((level_total + pts))
            fi
        done

        echo -e "  >> ${YELLOW}Level Total:${RESET} $level_total"
        echo ""
    fi
done

total=$(awk -F: '{sum+=$2} END{print sum}' "$PROGRESS")

echo -e "${YELLOW}======================================"
echo -e "🎯 Total Points: $total"
echo -e "======================================${RESET}"
