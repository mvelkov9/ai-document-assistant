#!/usr/bin/env bash
set -eu

RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-7}"
BACKUP_ROOT="${BACKUP_ROOT:-./backups}"
timestamp="$(date +%Y%m%d-%H%M%S)"
backup_dir="$BACKUP_ROOT/$timestamp"

mkdir -p "$backup_dir"

if [[ ! -f .env ]]; then
  echo "Missing .env file. Copy .env.example to .env first."
  exit 1
fi

set -a
. ./.env
set +a

COMPOSE="docker compose -f docker-compose.yml -f docker-compose.prod.yml"

echo "==> Creating PostgreSQL backup..."
$COMPOSE exec -T postgres \
  pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" > "$backup_dir/postgres.sql"

echo "==> Creating MinIO backup archive..."
$COMPOSE exec -T minio \
  tar -czf - /data > "$backup_dir/minio-data.tar.gz"

# ── GPG symmetric encryption ──
if [[ -n "${BACKUP_PASSPHRASE:-}" ]]; then
  echo "==> Encrypting backups with GPG..."
  for f in "$backup_dir"/postgres.sql "$backup_dir"/minio-data.tar.gz; do
    gpg --batch --yes --symmetric --cipher-algo AES256 \
      --passphrase "$BACKUP_PASSPHRASE" "$f"
    rm -f "$f"
  done
  echo "   Encrypted files: $(ls "$backup_dir"/*.gpg 2>/dev/null | wc -l)"
else
  echo "   BACKUP_PASSPHRASE not set — skipping encryption."
fi

# ── Verify backup ──
echo "==> Verifying backup..."
file_count=$(find "$backup_dir" -type f | wc -l)
if [[ "$file_count" -lt 2 ]]; then
  echo "FAIL: Expected at least 2 backup files, found $file_count."
  exit 1
fi
echo "   OK: $file_count files in $backup_dir"

# ── Rotate old backups ──
echo "==> Rotating backups older than ${RETENTION_DAYS} days..."
deleted=$(find "$BACKUP_ROOT" -maxdepth 1 -mindepth 1 -type d -mtime +"$RETENTION_DAYS" -print -exec rm -rf {} + | wc -l)
echo "   Deleted $deleted old backup(s)."

echo "==> Backup complete: $backup_dir"
