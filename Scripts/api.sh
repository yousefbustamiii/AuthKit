#!/bin/sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
ROOT_DIR=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)
PYTHON_BIN="$ROOT_DIR/server/.venv/bin/python"

if [ ! -x "$PYTHON_BIN" ]; then
  echo "Missing server virtualenv at $PYTHON_BIN" >&2
  exit 1
fi

cd "$ROOT_DIR"
exec "$PYTHON_BIN" -m uvicorn server.main:app --host 0.0.0.0 --port 8000 --workers 1 --loop uvloop
