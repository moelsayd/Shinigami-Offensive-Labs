#!/bin/bash
ROOM="$(cd "$(dirname "$0")" && pwd)"
[ -f "$ROOM/.web.pid" ] && kill $(cat "$ROOM/.web.pid") 2>/dev/null
[ -f "$ROOM/.ssh.pid" ] && kill $(cat "$ROOM/.ssh.pid") 2>/dev/null
[ -f "$ROOM/.db.pid" ] && kill $(cat "$ROOM/.db.pid") 2>/dev/null
pkill -f "web_server.py 7501" 2>/dev/null
pkill -f "ssh_server.py 7502" 2>/dev/null
pkill -f "db_server.py 7503" 2>/dev/null
rm -f "$ROOM/.web.pid" "$ROOM/.ssh.pid" "$ROOM/.db.pid"
echo "Room stopped."
