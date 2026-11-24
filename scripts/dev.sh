#!/usr/bin/env bash
# Runs the API (port 8000) and the frontend (port 5173) together. Ctrl+C stops both.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

pids=()
trap 'kill "${pids[@]}" 2>/dev/null || true' EXIT INT TERM

(cd "$ROOT/backend" && exec .venv/bin/uvicorn app.main:app --reload --reload-dir app --port 8000) &
pids+=($!)
(cd "$ROOT/frontend" && exec node_modules/.bin/vite) &
pids+=($!)

echo "API:      http://127.0.0.1:8000/docs"
echo "Frontend: http://localhost:5173"
wait -n || true
