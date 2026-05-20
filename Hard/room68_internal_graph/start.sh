#!/bin/bash
ROOM="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOM"
pkill -f "reverse_proxy.py 10801" 2>/dev/null; pkill -f "metadata.py 10820" 2>/dev/null; pkill -f "internal_api.py 10833" 2>/dev/null; pkill -f "db_server.py 10847" 2>/dev/null
sleep 1
python3 reverse_proxy.py 10801 & echo $! > .proxy.pid
python3 metadata.py 10820 & echo $! > .meta.pid
python3 internal_api.py 10833 & echo $! > .api.pid
python3 db_server.py 10847 & echo $! > .db.pid
sleep 2
curl -s http://127.0.0.1:10801/ | grep -q "CorpNet Portal" && echo "Room initialized. Discover the services."
