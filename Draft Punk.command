#!/bin/bash
# Double-click this file to launch the Markdown editor.
# Starts the local server if it isn't already running, then opens your browser.

DIR="$(cd "$(dirname "$0")" && pwd)"
PORT=8787

if ! curl -s -o /dev/null "http://localhost:$PORT/" 2>/dev/null; then
  echo "Starting Draft Punk server..."
  nohup python3 "$DIR/server.py" > "$DIR/server.log" 2>&1 &
  for _ in $(seq 1 20); do
    curl -s -o /dev/null "http://localhost:$PORT/" 2>/dev/null && break
    sleep 0.25
  done
fi

if curl -s -o /dev/null "http://localhost:$PORT/" 2>/dev/null; then
  open "http://localhost:$PORT/${1:+?file=$1}"
  echo "Draft Punk is open at http://localhost:$PORT"
else
  echo "Server failed to start. Check $DIR/server.log"
  read -r -p "Press Return to close..."
fi
