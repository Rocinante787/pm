#!/usr/bin/env bash
set -e

if command -v docker >/dev/null 2>&1; then
  echo "Stopping pm-app container..."
  docker stop pm-app 2>/dev/null || true
  docker rm pm-app 2>/dev/null || true
  echo "pm-app container stopped."
else
  echo "Stopping local uvicorn processes..."
  pkill -f "uvicorn app.main:app" 2>/dev/null || true
  echo "Stopped."
fi

