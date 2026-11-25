#!/usr/bin/env bash
# Prepares local PostgreSQL for AI Learning Lab: low-memory tuning, role, databases, backend/.env.
# Safe to re-run. Each run sets a NEW random password for the "ailab" role and rewrites DATABASE_URL.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="$ROOT/backend/.env"
cd /tmp

PGCONF_DIR="$(ls -d /etc/postgresql/*/main 2>/dev/null | sort -V | tail -n 1 || true)"
[ -n "$PGCONF_DIR" ] || { echo "No PostgreSQL cluster found under /etc/postgresql."; exit 1; }

echo ">> Applying low-memory PostgreSQL settings ($PGCONF_DIR/conf.d/ailab.conf)"
sudo mkdir -p "$PGCONF_DIR/conf.d"
sudo tee "$PGCONF_DIR/conf.d/ailab.conf" >/dev/null <<'CONF'
# AI Learning Lab: tuned for a machine with little RAM.
shared_buffers = 64MB
work_mem = 4MB
maintenance_work_mem = 32MB
effective_cache_size = 256MB
max_connections = 20
wal_buffers = 4MB
max_wal_size = 512MB
CONF
sudo systemctl restart postgresql
for _ in $(seq 1 30); do
  sudo -u postgres psql -qAtc "SELECT 1" >/dev/null 2>&1 && break
  sleep 1
done
sudo -u postgres psql -qAtc "SELECT 1" >/dev/null

PORT="$(sudo -u postgres psql -qAtc 'SHOW port')"
DB_PASS="$(openssl rand -hex 16)"

echo ">> Creating role and databases (port $PORT)"
sudo -u postgres psql -q -v ON_ERROR_STOP=1 -v pw="$DB_PASS" <<'SQL'
SELECT 'CREATE ROLE ailab LOGIN' WHERE NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'ailab') \gexec
ALTER ROLE ailab WITH PASSWORD :'pw';
SELECT 'CREATE DATABASE ailab OWNER ailab' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'ailab') \gexec
SELECT 'CREATE DATABASE ailab_test OWNER ailab' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'ailab_test') \gexec
SQL

PGPASSWORD="$DB_PASS" psql -h 127.0.0.1 -p "$PORT" -U ailab -d ailab -qAtc "SELECT 'database connection OK'"

touch "$ENV_FILE"
set_env() {
  grep -v "^$1=" "$ENV_FILE" > "$ENV_FILE.tmp" || true
  echo "$1=$2" >> "$ENV_FILE.tmp"
  mv "$ENV_FILE.tmp" "$ENV_FILE"
}
set_env DATABASE_URL "postgresql+psycopg://ailab:${DB_PASS}@127.0.0.1:${PORT}/ailab"
grep -q '^JWT_SECRET=.\{32,\}' "$ENV_FILE" || set_env JWT_SECRET "$(openssl rand -hex 32)"
set_env COOKIE_SECURE false
chmod 600 "$ENV_FILE"
echo ">> Wrote DATABASE_URL, JWT_SECRET and COOKIE_SECURE to backend/.env (git-ignored)."
