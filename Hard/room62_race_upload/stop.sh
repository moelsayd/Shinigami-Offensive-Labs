#!/bin/bash
ROOM="$(cd "$(dirname "$0")" && pwd)"
[ -f "$ROOM/.web.pid" ] && kill $(cat "$ROOM/.web.pid") 2>/dev/null
[ -f "$ROOM/.ssh.pid" ] && kill $(cat "$ROOM/.ssh.pid") 2>/dev/null
pkill -f "web_race.py 9701" 2>/dev/null; pkill -f "ssh_sim.py 9702" 2>/dev/null
rm -f "$ROOM/.web.pid" "$ROOM/.ssh.pid"
echo "Room stopped."
