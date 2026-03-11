# Production Rollout Checklist

## Purpose

This checklist defines the minimal production rollout path for deploying the application to the personal VPS and validating that the deployment is stable enough for demonstration and grading.

## Before deployment

1. Verify that Docker and Docker Compose work for the active VPS user.
2. Copy `.env.example` to `.env` and replace production secrets.
3. Confirm that the domain or IP points to the VPS.
4. Check that ports 80 and 443 are available on the host.
5. Verify that PostgreSQL and MinIO data volumes are persistent.

## Deployment steps

1. Pull the latest repository state.
2. Run `infrastructure/scripts/deploy.sh` from the repository root.
3. The deploy script will:
   - Pull latest images
   - Build and start all services
   - Run `alembic upgrade head` inside the backend container
   - Poll `/health` endpoint (15 retries, 2s interval)
   - Display service status on success or backend logs on failure
4. Verify container status with `docker compose -f docker-compose.yml -f docker-compose.prod.yml ps`.
5. Open `/health`, `/ready`, `/docs`, and `/redoc` through the reverse proxy.
6. Seed demo data if needed: `docker compose exec backend python scripts/seed_demo.py`.

## Post-deployment checks

1. Confirm that the frontend is reachable through the reverse proxy.
2. Confirm that `/docs` and `/redoc` load correctly with endpoint descriptions and examples.
3. Confirm security headers are present: `curl -I http://localhost/health`.
4. Confirm login works with the demo account.
5. Confirm document listing works with pagination.
6. Confirm summary job creation and polling work.
7. Confirm question-answer flow works.
8. Confirm rate limiting works: rapid requests should return 429.
9. Run `infrastructure/scripts/backup.sh` once to validate backup access.

## Failure handling

1. If `/ready` fails, inspect database and MinIO health first.
2. If the frontend is blank, inspect the frontend container logs and reverse proxy configuration.
3. If auth fails, check backend logs and verify `SECRET_KEY` and database access.
4. If summary or Q&A jobs fail, inspect backend logs and AI configuration.

## Recommended evidence for defense

1. Screenshot or live demo of `/docs`.
2. Screenshot or live demo of the document dashboard.
3. Example of a completed summary job.
4. Example of a completed question job.
5. Example backup artifact or backup command output.
