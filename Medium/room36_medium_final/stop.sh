#!/usr/bin/env bash
ROOM="$(cd "$(dirname "$0")" && pwd)"
[ -f "$ROOM/.web.pid" ] && kill $(cat "$ROOM/.web.pid") 2>/dev/null
[ -f "$ROOM/.ssh.pid" ] && kill $(cat "$ROOM/.ssh.pid") 2>/dev/null
pkill -f "python3 web_server.py 6088" 2>/dev/null
pkill -f "python3 ssh_server.py 6089" 2>/dev/null
rm -f "$ROOM/.web.pid" "$ROOM/.ssh.pid"
echo "Services stopped."
