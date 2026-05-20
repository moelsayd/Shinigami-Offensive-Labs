#!/bin/bash
echo "Resetting room..."
pkill -f "http.server"
python3 -m http.server 8000 &
