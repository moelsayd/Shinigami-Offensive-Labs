#!/usr/bin/env bash
ROOM_DIR="$(cd "$(dirname "$0")" && pwd)"
for pidfile in .pid_web .pid_tcp; do
    [ -f "$ROOM_DIR/$pidfile" ] && kill $(cat "$ROOM_DIR/$pidfile") 2>/dev/null
done
pkill -f "python3 jwt_server.py 6070" 2>/dev/null
pkill -f "python3 tcp_server.py 6071" 2>/dev/null
rm -f "$ROOM_DIR/.pid_web" "$ROOM_DIR/.pid_tcp"
echo "Services stopped."
