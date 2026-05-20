#!/bin/bash
ROOM="$(cd "$(dirname "$0")" && pwd)"
for f in .proxy.pid .mob.pid .int.pid .work.pid .mon.pid; do
    [ -f "$ROOM/$f" ] && kill $(cat "$ROOM/$f") 2>/dev/null
done
pkill -f "reverse_proxy.py 11381" 2>/dev/null; pkill -f "mobile_api.py 11423" 2>/dev/null; pkill -f "internal_api.py 11507" 2>/dev/null; pkill -f "worker.py 11642" 2>/dev/null; pkill -f "monitoring.py 11739" 2>/dev/null
rm -f "$ROOM/.proxy.pid" "$ROOM/.mob.pid" "$ROOM/.int.pid" "$ROOM/.work.pid" "$ROOM/.mon.pid"
echo "Room stopped."
