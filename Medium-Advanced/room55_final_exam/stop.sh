#!/bin/bash
ROOM="$(cd "$(dirname "$0")" && pwd)"
[ -f "$ROOM/.web.pid" ] && kill $(cat "$ROOM/.web.pid") 2>/dev/null
[ -f "$ROOM/.api.pid" ] && kill $(cat "$ROOM/.api.pid") 2>/dev/null
[ -f "$ROOM/.ssh.pid" ] && kill $(cat "$ROOM/.ssh.pid") 2>/dev/null
pkill -f "web_main.py 8901" 2>/dev/null; pkill -f "api_server.py 8902" 2>/dev/null; pkill -f "ssh_sim.py 8903" 2>/dev/null
rm -f "$ROOM/.web.pid" "$ROOM/.api.pid" "$ROOM/.ssh.pid"
echo "Room stopped."
