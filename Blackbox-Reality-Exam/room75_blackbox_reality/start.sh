#!/bin/bash
ROOM="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOM"
pkill -f "reverse_proxy.py 13001" 2>/dev/null; pkill -f "auth_service.py 13002" 2>/dev/null; pkill -f "user_service.py 13003" 2>/dev/null; pkill -f "billing_service.py 13004" 2>/dev/null; pkill -f "legacy_service.py 13005" 2>/dev/null; pkill -f "worker.py 13006" 2>/dev/null; pkill -f "monitoring.py 13007" 2>/dev/null
sleep 1
python3 reverse_proxy.py 13001 & echo $! > .proxy.pid
python3 auth_service.py 13002 & echo $! > .auth.pid
python3 user_service.py 13003 & echo $! > .user.pid
python3 billing_service.py 13004 & echo $! > .bill.pid
python3 legacy_service.py 13005 & echo $! > .legacy.pid
python3 worker.py 13006 & echo $! > .work.pid
python3 monitoring.py 13007 & echo $! > .mon.pid
sleep 2
curl -s http://127.0.0.1:13001/ | grep -q "Corporate Portal" && echo "Room initialized. Discover the services."
