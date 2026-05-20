#!/bin/bash
ROOM="$(cd "$(dirname "$0")" && pwd)"
[ -f "$ROOM/.web.pid" ] && kill $(cat "$ROOM/.web.pid") 2>/dev/null
[ -f "$ROOM/.api.pid" ] && kill $(cat "$ROOM/.api.pid") 2>/dev/null
[ -f "$ROOM/.ssh.pid" ] && kill $(cat "$ROOM/.ssh.pid") 2>/dev/null
[ -f "$ROOM/.ws.pid" ] && kill $(cat "$ROOM/.ws.pid") 2>/dev/null
pkill -f "web_main.py 10010" 2>/dev/null; pkill -f "api_internal.py 10020" 2>/dev/null
pkill -f "ssh_sim.py 10030" 2>/dev/null; pkill -f "ws_server.py 10040" 2>/dev/null
rm -f "$ROOM/.web.pid" "$ROOM/.api.pid" "$ROOM/.ssh.pid" "$ROOM/.ws.pid"
echo "Room stopped."
