#!/usr/bin/env bash
ROOM_DIR="$(cd "$(dirname "$0")" && pwd)"
for pidfile in .web.pid .ssh.pid; do
    [ -f "$ROOM_DIR/$pidfile" ] && kill $(cat "$ROOM_DIR/$pidfile") 2>/dev/null
done
pkill -f "python3 web_server.py 6072" 2>/dev/null
pkill -f "python3 ssh_simulator.py 6073" 2>/dev/null
rm -f "$ROOM_DIR/.web.pid" "$ROOM_DIR/.ssh.pid"
echo "Services stopped."
