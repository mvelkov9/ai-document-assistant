#!/usr/bin/env bash
set -eu

COMPOSE="docker compose -f docker-compose.yml -f docker-compose.prod.yml"

if [[ ! -f .env ]]; then
  echo "Missing .env file. Copy .env.example to .env first."
  exit 1
fi

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker is required for deployment."
  exit 1
fi

echo "==> Pulling latest images..."
$COMPOSE pull || true

echo "==> Building and starting services..."
$COMPOSE up -d --build

echo "==> Running database migrations..."
$COMPOSE exec -T backend alembic upgrade head || echo "WARN: Alembic migration skipped (may not be available yet)"

echo "==> Waiting for health check..."
RETRIES=15
for i in $(seq 1 $RETRIES); do
  if curl -sf http://localhost/health > /dev/null 2>&1; then
    echo "OK: Backend healthy after $i attempt(s)."
    break
  fi
  if [ "$i" -eq "$RETRIES" ]; then
    echo "FAIL: Backend did not become healthy after $RETRIES attempts."
    $COMPOSE logs --tail=30 backend
    exit 1
  fi
  sleep 2
done

echo "==> Service status:"
$COMPOSE ps

echo "Deployment complete."

