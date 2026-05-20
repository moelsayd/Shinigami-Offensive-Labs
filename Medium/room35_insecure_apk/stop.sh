#!/usr/bin/env bash
ROOM="$(cd "$(dirname "$0")" && pwd)"
[ -f "$ROOM/.adb.pid" ] && kill $(cat "$ROOM/.adb.pid") 2>/dev/null
[ -f "$ROOM/.web.pid" ] && kill $(cat "$ROOM/.web.pid") 2>/dev/null
pkill -f "adb_sim.py 5556" 2>/dev/null
pkill -f "secret_server.py 9999" 2>/dev/null
rm -f "$ROOM/.adb.pid" "$ROOM/.web.pid" "$ROOM/fake_app.apk"
echo "Services stopped."
