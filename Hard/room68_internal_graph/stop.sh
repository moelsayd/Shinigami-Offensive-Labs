#!/bin/bash
ROOM="$(cd "$(dirname "$0")" && pwd)"
for f in .proxy.pid .meta.pid .api.pid .db.pid; do
    [ -f "$ROOM/$f" ] && kill $(cat "$ROOM/$f") 2>/dev/null
done
pkill -f "reverse_proxy.py 10801" 2>/dev/null; pkill -f "metadata.py 10820" 2>/dev/null; pkill -f "internal_api.py 10833" 2>/dev/null; pkill -f "db_server.py 10847" 2>/dev/null
rm -f "$ROOM/.proxy.pid" "$ROOM/.meta.pid" "$ROOM/.api.pid" "$ROOM/.db.pid"
echo "Room stopped."
