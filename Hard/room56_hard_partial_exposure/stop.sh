#!/bin/bash
ROOM="$(cd "$(dirname "$0")" && pwd)"
[ -f "$ROOM/.web.pid" ] && kill $(cat "$ROOM/.web.pid") 2>/dev/null
[ -f "$ROOM/.deser.pid" ] && kill $(cat "$ROOM/.deser.pid") 2>/dev/null
[ -f "$ROOM/.ssh.pid" ] && kill $(cat "$ROOM/.ssh.pid") 2>/dev/null
pkill -f "web_server.py 9101" 2>/dev/null; pkill -f "deser_server.py 9102" 2>/dev/null; pkill -f "ssh_sim.py 9103" 2>/dev/null
rm -f "$ROOM/.web.pid" "$ROOM/.deser.pid" "$ROOM/.ssh.pid"
echo "Room stopped."
