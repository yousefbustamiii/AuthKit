#!/bin/sh
set -eu

PORT=3000

pids=$(lsof -ti tcp:"$PORT" || true)

if [ -z "$pids" ]; then
  echo "Nothing is running on port $PORT."
  exit 0
fi

kill -TERM $pids 2>/dev/null || true
sleep 1

remaining=$(lsof -ti tcp:"$PORT" || true)
if [ -n "$remaining" ]; then
  kill -KILL $remaining 2>/dev/null || true
fi

echo "Stopped processes on port $PORT."
