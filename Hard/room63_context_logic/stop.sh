#!/bin/bash
ROOM="$(cd "$(dirname "$0")" && pwd)"
[ -f "$ROOM/.web.pid" ] && kill $(cat "$ROOM/.web.pid") 2>/dev/null
[ -f "$ROOM/.yaml.pid" ] && kill $(cat "$ROOM/.yaml.pid") 2>/dev/null
[ -f "$ROOM/.ssh.pid" ] && kill $(cat "$ROOM/.ssh.pid") 2>/dev/null
pkill -f "web_context.py 9801" 2>/dev/null; pkill -f "yaml_server.py 9802" 2>/dev/null; pkill -f "ssh_sim.py 9803" 2>/dev/null
rm -f "$ROOM/.web.pid" "$ROOM/.yaml.pid" "$ROOM/.ssh.pid"
echo "Room stopped."
