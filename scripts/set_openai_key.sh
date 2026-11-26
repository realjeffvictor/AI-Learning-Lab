#!/usr/bin/env bash
# Stores your OpenAI API key in backend/.env (git-ignored) without echoing it or putting it in shell history.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="$ROOT/backend/.env"
[ -f "$ENV_FILE" ] || { echo "backend/.env not found. Run ./scripts/setup_db.sh first."; exit 1; }

read -r -s -p "Paste your OpenAI API key (hidden): " KEY
echo
[ -n "$KEY" ] || { echo "No key entered."; exit 1; }
case "$KEY" in *[[:space:]]*) echo "The key must not contain spaces."; exit 1 ;; esac
read -r -p "Model name (see https://platform.openai.com/docs/models) [gpt-4o-mini]: " MODEL
MODEL="${MODEL:-gpt-4o-mini}"

set_env() {
  grep -v "^$1=" "$ENV_FILE" > "$ENV_FILE.tmp" || true
  echo "$1=$2" >> "$ENV_FILE.tmp"
  mv "$ENV_FILE.tmp" "$ENV_FILE"
}
set_env OPENAI_API_KEY "$KEY"
set_env OPENAI_MODEL "$MODEL"
chmod 600 "$ENV_FILE"
echo "Saved to backend/.env (git-ignored). Restart the API to apply it."
