#!/usr/bin/env bash
BASE="$HOME/ctf-labs"
PROGRESS="$BASE/progress.txt"

# ---------- Colors ----------
GREEN='\e[1;32m'
YELLOW='\e[1;33m'
ORANGE='\e[38;5;208m'
RED='\e[1;31m'
PURPLE='\e[38;5;93m'
CYAN='\e[1;36m'
RESET='\e[0m'

# ---------- Init ----------
touch "$PROGRESS" 2>/dev/null

# ---------- Progression Helpers ----------
room_completed() {
    local room_name="$1"
    grep -q "^${room_name}:" "$PROGRESS" 2>/dev/null
}

can_enter_room() {
    local room_path="$1"
    local room_name=$(basename "$room_path")
    local level_dir=$(dirname "$room_path")

    local num=$(echo "$room_name" | sed -n 's/^room\([0-9][0-9]*\).*/\1/p')
    if [ -z "$num" ]; then
        return 1
    fi
    if [ "$num" -eq 1 ]; then
        return 0
    fi
    local prev_num=$((num - 1))
    local prev_room=""
    for d in "$level_dir"/room"${prev_num}"_*; do
        if [ -d "$d" ]; then
            prev_room="$d"
            break
        fi
    done
    if [ -z "$prev_room" ]; then
        return 0
    fi
    local prev_name=$(basename "$prev_room")
    room_completed "$prev_name"
}

can_enter_level() {
    local level_dir="$1"
    local level_name=$(basename "$level_dir")

    # المستويات الخاصة (Android-Exam, Blackbox-Reality-Exam) مفتوحة دائمًا
    if [ "$level_name" = "Android-Exam" ] || [ "$level_name" = "Blackbox-Reality-Exam" ]; then
        return 0
    fi

    if [ "$level_name" = "Easy" ]; then
        return 0
    fi

    case "$level_name" in
        Medium) prev_level="Easy" ;;
        Medium-Advanced) prev_level="Medium" ;;
        Hard) prev_level="Medium-Advanced" ;;
        *) return 0 ;;
    esac

    local prev_dir="$BASE/$prev_level"
    [ ! -d "$prev_dir" ] && return 0

    local last_room=""
    for d in "$prev_dir"/room*; do
        [ -d "$d" ] && last_room="$d"
    done
    if [ -z "$last_room" ]; then
        return 0
    fi
    local last_name=$(basename "$last_room")
    room_completed "$last_name"
}

# ---------- Support Banner ----------
support_banner() {
    local tips=(
        "🧠 Enumeration > Exploitation"
        "⚡ Check hidden endpoints."
        "🔍 Always inspect response headers."
        "💜 Community-supported offensive security labs."
        "🔥 Real hackers build their own tools."
        "📡 Every leak is a node in a graph."
        "☠ Support keeps new enterprise rooms alive."
        "⚙ Realistic labs require real infrastructure."
    )
    echo ""
    echo -e "${PURPLE}╔══════════════════════════════════════╗${RESET}"
    echo -e "${PURPLE}║${RESET} ${CYAN}Shinigami RedTeam Labs v1.0${RESET}       ${PURPLE}║${RESET}"
    echo -e "${PURPLE}║${RESET} ${YELLOW}Community Offensive Security Labs${RESET}  ${PURPLE}║${RESET}"
    echo -e "${PURPLE}║${RESET} ${GREEN}Support & Contributions: 01093963670${RESET} ${PURPLE}║${RESET}"
    echo -e "${PURPLE}╚══════════════════════════════════════╝${RESET}"
    echo -e "${CYAN}${tips[$RANDOM % ${#tips[@]}]}${RESET}"
    echo ""
}

# ---------- Room Runner ----------
show_room() {
    local room="$1"
    local room_name=$(basename "$room")
    local stop_script="$room/stop.sh"
    local start_script="$room/start.sh"

    [ -f "$stop_script" ] && bash "$stop_script" &>/dev/null

    clear
    echo -e "${CYAN}☠️  $room_name${RESET}"
    echo "================================="

    if [ -f "$start_script" ]; then
        bash "$start_script"
        if [ $? -ne 0 ]; then
            read -p "Target start failed. Press Enter to return..."
            return
        fi
    fi

    [ -f "$room/tasks.txt" ] && { echo -e "\n📜 Tasks:"; cat "$room/tasks.txt"; }

    echo ""
    echo "--- Actions ---"
    echo "f) Submit flag"
    echo "h) Show hints"
    echo "r) Restart target"
    if grep -q "PORT=" "$start_script" 2>/dev/null; then
        echo "t) Test connection to target"
    else
        echo "t) (not available)"
    fi
    echo "s) Stop target & return"
    echo "q) Back to level menu"
    echo "======================"

    while true; do
        read -p "Action: " action
        case "$action" in
            f)
                if [ -f "$room/submit_flag.sh" ]; then
                    bash "$room/submit_flag.sh"
                    support_banner
                else
                    echo "No submit script."
                fi
                ;;
            h) [ -f "$room/hints.txt" ] && cat "$room/hints.txt" || echo "No hints." ;;
            r)
                [ -f "$stop_script" ] && bash "$stop_script" &>/dev/null
                [ -f "$start_script" ] && bash "$start_script"
                ;;
            t)
                # استخراج المنفذ بأمان باستخدام sed (لا يعتمد على grep -P)
                local port=$(grep -o '[0-9]\+' <<< "$(grep 'PORT=' "$start_script" 2>/dev/null)" | head -1)
                if [ -n "$port" ]; then
                    echo "🔍 Testing http://localhost:$port ..."
                    curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" --connect-timeout 3 "http://localhost:$port" || echo "❌ Cannot reach target."
                else
                    echo "⚠️  This action is only for network-based rooms."
                fi
                ;;
            s) [ -f "$stop_script" ] && bash "$stop_script"; break ;;
            q) return ;;
            *) echo "Unknown action." ;;
        esac
    done
}

# ---------- Level Scoreboard ----------
level_scoreboard() {
    local level_dir="$1"
    local level_name=$(basename "$level_dir")
    local total=0

    echo -e "${CYAN}📊 Scoreboard for $level_name Level${RESET}"
    echo "----------------------------------------"

    if [ ! -s "$PROGRESS" ]; then
        echo "No progress recorded yet."
    else
        for room_path in "$level_dir"/room*; do
            [ -d "$room_path" ] || continue
            local rname=$(basename "$room_path")
            local points=$(grep "^${rname}:" "$PROGRESS" 2>/dev/null | cut -d: -f2)
            if [ -n "$points" ]; then
                echo "$rname : $points"
                total=$((total + points))
            fi
        done
        echo "----------------------------------------"
        echo "Total Points: $total"
    fi
    echo ""
    support_banner
}

# ---------- Level Menu ----------
level_menu() {
    local level_dir="$1"
    local level_name=$(basename "$level_dir")

    if ! can_enter_level "$level_dir"; then
        echo -e "${RED}🔒 Level $level_name is locked. Complete the previous level's final exam first.${RESET}"
        read -p "Press Enter to continue..."
        return
    fi

    # ترتيب الغرف رقميًا (1,2,...,10,11) بدلاً من الأبجدي (1,10,11,2,...)
    local rooms=()
    while IFS= read -r path; do
        rooms+=("$path")
    done < <(for d in "$level_dir"/room*; do
        echo "$d"
    done | while read -r p; do
        n=$(basename "$p" | sed -n 's/^room\([0-9]\+\)_.*/\1/p')
        printf "%08d %s\n" "$n" "$p"
    done | sort -n | cut -d' ' -f2-)

    while true; do
        clear
        echo -e "${CYAN}===================================${RESET}"
        echo -e "${CYAN}☠️  Shinigami CTF Lab - ${level_name} Level${RESET}"
        echo -e "${CYAN}===================================${RESET}"

        local index=1
        for room_path in "${rooms[@]}"; do
            local room_name=$(basename "$room_path")
            local locked=""
            if ! can_enter_room "$room_path"; then
                locked=" 🔒"
            fi
            echo "$index) $room_name$locked"
            index=$((index + 1))
        done

        echo ""
        echo "s) 📊 Level Scoreboard"
        echo "b) 🔙 Back to level selection"
        echo "q) Quit lab"
        echo "============================================="

        read -p "Choose: " choice
        case "$choice" in
            q) exit 0 ;;
            b) return ;;
            s) level_scoreboard "$level_dir"; read -p "Press Enter to continue..." ;;
            *)
                if [[ "$choice" =~ ^[0-9]+$ ]] && [ "$choice" -ge 1 ] && [ "$choice" -le "${#rooms[@]}" ]; then
                    local room_path="${rooms[$((choice-1))]}"
                    if can_enter_room "$room_path"; then
                        show_room "$room_path"
                    else
                        echo -e "${RED}🔒 You must complete the previous room first.${RESET}"
                        sleep 2
                    fi
                else
                    echo "Invalid option."
                    sleep 1
                fi
                ;;
        esac
    done
}

# ---------- Overall Scoreboard ----------
overall_scoreboard() {
    clear
    echo -e "${CYAN}===================================${RESET}"
    echo -e "${CYAN}=== 🏆 Overall Shinigami CTF Progress ===${RESET}"
    echo -e "${CYAN}===================================${RESET}"
    if [ ! -s "$PROGRESS" ]; then
        echo "No progress recorded yet."
    else
        cat "$PROGRESS"
        total=$(awk -F: '{sum+=$2} END{print sum}' "$PROGRESS" 2>/dev/null)
        echo "----------------------------------------"
        echo "Total Points: $total"
    fi
    echo ""
    support_banner
}

# ---------- Main Menu ----------
while true; do
    clear
    echo -e "${PURPLE}╔══════════════════════════════════════╗${RESET}"
    echo -e "${PURPLE}║${RESET}   ${CYAN}☠️  Shinigami Offensive Labs ☠️${RESET}   ${PURPLE}║${RESET}"
    echo -e "${PURPLE}╚══════════════════════════════════════╝${RESET}"
    echo ""
    echo -e "${GREEN}1) Easy${RESET}"
    echo -e "${YELLOW}2) Medium${RESET}"
    echo -e "${ORANGE}3) Medium-Advanced${RESET}"
    echo -e "${RED}4) Hard${RESET}"
    echo -e "${PURPLE}5) Android-Exam${RESET}"
    echo -e "${PURPLE}6) Blackbox-Reality-Exam${RESET}"
    echo ""
    echo "s) 📊 Overall Scoreboard"
    echo "r) 🔄 Reset all progress"
    echo "q) Quit"
    read -p "Choose: " choice

    case "$choice" in
        1) level_menu "$BASE/Easy" ;;
        2) level_menu "$BASE/Medium" ;;
        3) level_menu "$BASE/Medium-Advanced" ;;
        4) level_menu "$BASE/Hard" ;;
        5) level_menu "$BASE/Android-Exam" ;;
        6) level_menu "$BASE/Blackbox-Reality-Exam" ;;
        s) overall_scoreboard; read -p "Press Enter to return..." ;;
        r)
            read -p "Are you sure you want to delete ALL progress? (yes/no): " confirm
            if [ "$confirm" = "yes" ]; then
                rm -f "$PROGRESS"
                touch "$PROGRESS"
                echo -e "${RED}🗑️  All progress has been reset.${RESET}"
            else
                echo "Reset cancelled."
            fi
            read -p "Press Enter to continue..."
            ;;
        q) exit 0 ;;
        *) sleep 1 ;;
    esac
done
