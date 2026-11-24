#!/usr/bin/env bash
# One-time setup on a fresh clone: backend venv + locked Python deps, frontend deps from the lockfile.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cd "$ROOT/backend"
[ -d .venv ] || python3 -m venv .venv
.venv/bin/python -m pip install --quiet --upgrade pip
.venv/bin/pip install --only-binary=:all: -r requirements.lock
[ -f .env ] || cp .env.example .env

cd "$ROOT/frontend"
NODE_OPTIONS=--max-old-space-size=1536 npm ci --no-audit --no-fund

echo "Bootstrap complete. Run ./scripts/dev.sh"
