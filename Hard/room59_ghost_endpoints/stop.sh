#!/bin/bash
ROOM="$(cd "$(dirname "$0")" && pwd)"
[ -f "$ROOM/.web.pid" ] && kill $(cat "$ROOM/.web.pid") 2>/dev/null
[ -f "$ROOM/.cache.pid" ] && kill $(cat "$ROOM/.cache.pid") 2>/dev/null
[ -f "$ROOM/.ssh.pid" ] && kill $(cat "$ROOM/.ssh.pid") 2>/dev/null
pkill -f "web_ghost.py 9401" 2>/dev/null; pkill -f "cache_server.py 9402" 2>/dev/null; pkill -f "ssh_sim.py 9403" 2>/dev/null
rm -f "$ROOM/.web.pid" "$ROOM/.cache.pid" "$ROOM/.ssh.pid"
echo "Room stopped."
