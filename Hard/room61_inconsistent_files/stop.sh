#!/bin/bash
ROOM="$(cd "$(dirname "$0")" && pwd)"
[ -f "$ROOM/.web.pid" ] && kill $(cat "$ROOM/.web.pid") 2>/dev/null
[ -f "$ROOM/.oracle.pid" ] && kill $(cat "$ROOM/.oracle.pid") 2>/dev/null
[ -f "$ROOM/.ssh.pid" ] && kill $(cat "$ROOM/.ssh.pid") 2>/dev/null
pkill -f "web_server.py 9601" 2>/dev/null; pkill -f "padding_oracle.py 9602" 2>/dev/null; pkill -f "ssh_sim.py 9603" 2>/dev/null
rm -f "$ROOM/.web.pid" "$ROOM/.oracle.pid" "$ROOM/.ssh.pid"
echo "Room stopped."
