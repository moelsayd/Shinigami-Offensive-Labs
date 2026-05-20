#!/bin/bash
ROOM="$(cd "$(dirname "$0")" && pwd)"
for f in .web.pid .mon.pid .work.pid .ssh.pid; do
    [ -f "$ROOM/$f" ] && kill $(cat "$ROOM/$f") 2>/dev/null
done
pkill -f "web_main.py 10901" 2>/dev/null; pkill -f "monitor_api.py 10922" 2>/dev/null; pkill -f "transaction_worker.py 10933" 2>/dev/null; pkill -f "ssh_sim.py 10944" 2>/dev/null
rm -f "$ROOM/.web.pid" "$ROOM/.mon.pid" "$ROOM/.work.pid" "$ROOM/.ssh.pid"
echo "Room stopped."
