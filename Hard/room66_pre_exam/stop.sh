#!/bin/bash
ROOM="$(cd "$(dirname "$0")" && pwd)"
[ -f "$ROOM/.web.pid" ] && kill $(cat "$ROOM/.web.pid") 2>/dev/null
[ -f "$ROOM/.worker.pid" ] && kill $(cat "$ROOM/.worker.pid") 2>/dev/null
[ -f "$ROOM/.ssh.pid" ] && kill $(cat "$ROOM/.ssh.pid") 2>/dev/null
pkill -f "graphql_main.py 10101" 2>/dev/null; pkill -f "async_worker.py 10102" 2>/dev/null; pkill -f "ssh_sim.py 10103" 2>/dev/null
rm -f "$ROOM/.web.pid" "$ROOM/.worker.pid" "$ROOM/.ssh.pid"
echo "Room stopped."
