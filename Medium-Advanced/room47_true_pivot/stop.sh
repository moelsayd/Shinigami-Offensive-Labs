#!/usr/bin/env bash
ROOM="$(cd "$(dirname "$0")" && pwd)"
[ -f "$ROOM/.web.pid" ] && kill $(cat "$ROOM/.web.pid") 2>/dev/null
[ -f "$ROOM/.ssh.pid" ] && kill $(cat "$ROOM/.ssh.pid") 2>/dev/null
pkill -f "web_jwt.py 8101" 2>/dev/null
pkill -f "ssh_sim.py 8103" 2>/dev/null
rm -f "$ROOM/.web.pid" "$ROOM/.ssh.pid"
echo "Room stopped."
