#!/bin/bash
ROOM="$(cd "$(dirname "$0")" && pwd)"
for f in .proxy.pid .auth.pid .user.pid .bill.pid .legacy.pid .work.pid .mon.pid; do
    [ -f "$ROOM/$f" ] && kill $(cat "$ROOM/$f") 2>/dev/null
done
pkill -f "reverse_proxy.py 13001" 2>/dev/null; pkill -f "auth_service.py 13002" 2>/dev/null; pkill -f "user_service.py 13003" 2>/dev/null; pkill -f "billing_service.py 13004" 2>/dev/null; pkill -f "legacy_service.py 13005" 2>/dev/null; pkill -f "worker.py 13006" 2>/dev/null; pkill -f "monitoring.py 13007" 2>/dev/null
rm -f "$ROOM/.proxy.pid" "$ROOM/.auth.pid" "$ROOM/.user.pid" "$ROOM/.bill.pid" "$ROOM/.legacy.pid" "$ROOM/.work.pid" "$ROOM/.mon.pid"
echo "Room stopped."
