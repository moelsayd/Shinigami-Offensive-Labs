#!/bin/bash
ROOM="$(cd "$(dirname "$0")" && pwd)"
for f in .proxy.pid .a.pid .b.pid .mon.pid; do
    [ -f "$ROOM/$f" ] && kill $(cat "$ROOM/$f") 2>/dev/null
done
pkill -f "reverse_proxy.py 11001" 2>/dev/null; pkill -f "service_a.py 11022" 2>/dev/null; pkill -f "service_b.py 11033" 2>/dev/null; pkill -f "monitoring.py 11044" 2>/dev/null
rm -f "$ROOM/.proxy.pid" "$ROOM/.a.pid" "$ROOM/.b.pid" "$ROOM/.mon.pid"
echo "Room stopped."
