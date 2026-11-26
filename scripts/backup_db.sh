#!/usr/bin/env bash
# Writes a compressed pg_dump to backups/ and keeps the newest BACKUP_KEEP files (default 14).
# Uses DATABASE_URL from the environment, or from backend/.env. Works against local or hosted PostgreSQL.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
URL="${DATABASE_URL:-}"
if [ -z "$URL" ] && [ -f "$ROOT/backend/.env" ]; then
  URL="$(grep -E '^DATABASE_URL=' "$ROOT/backend/.env" | head -1 | cut -d= -f2-)"
fi
[ -n "$URL" ] || { echo "DATABASE_URL is not set."; exit 1; }
URL="${URL/postgresql+psycopg:/postgresql:}"
URL="${URL/postgres:\/\//postgresql://}"

DIR="${BACKUP_DIR:-$ROOT/backups}"
KEEP="${BACKUP_KEEP:-14}"
mkdir -p "$DIR"
chmod 700 "$DIR"
OUT="$DIR/ailab-$(date -u +%Y%m%dT%H%M%SZ).sql.gz"
trap 'rm -f "$OUT"; echo "Backup failed."' ERR

pg_dump --no-owner --no-privileges "$URL" | gzip > "$OUT"
gzip -t "$OUT"
[ -s "$OUT" ] || { echo "Backup is empty."; exit 1; }
ls -1t "$DIR"/ailab-*.sql.gz | tail -n +"$((KEEP + 1))" | xargs -r rm -f --
echo "Backup written: $OUT ($(du -h "$OUT" | cut -f1)). Keeping the newest $KEEP."
