#!/usr/bin/env bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$DIR"

mkdir -p data

if command -v docker >/dev/null 2>&1; then
  echo "Building Docker image pm-app..."
  docker build -t pm-app .

  echo "Stopping existing pm-app container..."
  docker rm -f pm-app 2>/dev/null || true

  ENV_ARGS=""
  if [ -f ".env" ]; then
    ENV_ARGS="--env-file .env"
  fi

  echo "Starting pm-app container on port 8000..."
  docker run -d \
    --name pm-app \
    -p 8000:8000 \
    -v "$DIR/data:/app/data" \
    $ENV_ARGS \
    pm-app

  echo "App is running at http://localhost:8000"
else
  echo "Docker not detected. Starting locally with uv..."
  cd backend
  uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
fi
