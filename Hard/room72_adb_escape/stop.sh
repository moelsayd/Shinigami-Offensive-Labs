#!/bin/bash
ROOM="$(cd "$(dirname "$0")" && pwd)"
for f in .portal.pid .adb.pid .mon.pid; do
    [ -f "$ROOM/$f" ] && kill $(cat "$ROOM/$f") 2>/dev/null
done
pkill -f "web_portal.py 11201" 2>/dev/null
pkill -f "adb_sim.py 11222" 2>/dev/null
pkill -f "monitoring.py 11233" 2>/dev/null
rm -f "$ROOM/.portal.pid" "$ROOM/.adb.pid" "$ROOM/.mon.pid"
echo "Room stopped."
