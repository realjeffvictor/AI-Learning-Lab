#!/usr/bin/env bash
# Proves your newest backup restores: loads it into a scratch database, counts users, then drops it.
# Local PostgreSQL only (uses sudo -u postgres). A backup you have never restored is only a hope.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LATEST="$(ls -1t "$ROOT"/backups/ailab-*.sql.gz 2>/dev/null | head -1 || true)"
[ -n "$LATEST" ] || { echo "No backup found. Run scripts/backup_db.sh first."; exit 1; }
cd /tmp
SCRATCH=ailab_restore_check
echo ">> Restoring $LATEST into $SCRATCH"
sudo -u postgres dropdb --if-exists "$SCRATCH"
sudo -u postgres createdb "$SCRATCH"
trap 'sudo -u postgres dropdb --if-exists "$SCRATCH" >/dev/null 2>&1 || true' EXIT
gunzip -c "$LATEST" | sudo -u postgres psql -v ON_ERROR_STOP=1 -q "$SCRATCH" >/dev/null
USERS="$(sudo -u postgres psql -Atc 'SELECT count(*) FROM users' "$SCRATCH")"
LESSONS="$(sudo -u postgres psql -Atc 'SELECT count(*) FROM lessons' "$SCRATCH")"
echo "Restore OK: $USERS users, $LESSONS lessons. Scratch database dropped."
