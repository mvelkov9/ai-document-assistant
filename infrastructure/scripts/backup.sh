#!/usr/bin/env bash
set -eu

timestamp="$(date +%Y%m%d-%H%M%S)"
backup_dir="${1:-./backups/$timestamp}"

mkdir -p "$backup_dir"

if [[ ! -f .env ]]; then
  echo "Missing .env file. Copy .env.example to .env first."
  exit 1
fi

set -a
. ./.env
set +a

echo "Creating PostgreSQL backup in $backup_dir"
docker compose -f docker-compose.yml -f docker-compose.prod.yml exec -T postgres \
  pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" > "$backup_dir/postgres.sql"

echo "Creating MinIO backup archive in $backup_dir"
docker compose -f docker-compose.yml -f docker-compose.prod.yml exec -T minio \
  tar -czf - /data > "$backup_dir/minio-data.tar.gz"

echo "Backup finished: $backup_dir"
