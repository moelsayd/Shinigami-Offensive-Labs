#!/bin/bash
ROOM="$(cd "$(dirname "$0")" && pwd)"
for f in .proxy.pid .adb.pid .api.pid .mob.pid .work.pid .mon.pid; do
    [ -f "$ROOM/$f" ] && kill $(cat "$ROOM/$f") 2>/dev/null
done
pkill -f "reverse_proxy.py 12001" 2>/dev/null; pkill -f "adb_sim.py 12022" 2>/dev/null; pkill -f "internal_api.py 12033" 2>/dev/null; pkill -f "mobile_api.py 12044" 2>/dev/null; pkill -f "worker.py 12055" 2>/dev/null; pkill -f "monitoring.py 12066" 2>/dev/null
rm -f "$ROOM/.proxy.pid" "$ROOM/.adb.pid" "$ROOM/.api.pid" "$ROOM/.mob.pid" "$ROOM/.work.pid" "$ROOM/.mon.pid"
echo "Room stopped."
