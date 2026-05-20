#!/bin/bash
ROOM="$(cd "$(dirname "$0")" && pwd)"
[ -f "$ROOM/.web.pid" ] && kill $(cat "$ROOM/.web.pid") 2>/dev/null
[ -f "$ROOM/.xxe.pid" ] && kill $(cat "$ROOM/.xxe.pid") 2>/dev/null
[ -f "$ROOM/.ssh.pid" ] && kill $(cat "$ROOM/.ssh.pid") 2>/dev/null
pkill -f "web_logic.py 9501" 2>/dev/null; pkill -f "xxe_server.py 9502" 2>/dev/null; pkill -f "ssh_sim.py 9503" 2>/dev/null
rm -f "$ROOM/.web.pid" "$ROOM/.xxe.pid" "$ROOM/.ssh.pid"
echo "Room stopped."
