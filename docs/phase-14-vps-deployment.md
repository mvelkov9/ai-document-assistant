# Phase 14 - VPS Deployment Hardening

## Purpose

Move the repository closer to a production-ready VPS deployment by separating production settings and operational helper scripts from the local development path.

## Production deployment — COMPLETED 2026-03-11

The application is deployed and running in production:

| Detail | Value |
|--------|-------|
| Provider | Hetzner Cloud |
| Plan | CX33 (4 vCPU, 8 GB RAM, 80 GB disk) |
| OS | Ubuntu 24.04 LTS |
| IP | 178.104.25.28 |
| Domain | doc-ai-assist.com |
| TLS | Let's Encrypt (auto-renew via certbot timer) |
| Expires | 2026-06-09 |
| URL | https://doc-ai-assist.com |

All 5 containers running healthy: proxy (nginx with TLS), frontend, backend, postgres, minio.

## Implemented changes

- added `docker-compose.prod.yml` as a production overlay
- added restart policies and service health checks in the production overlay
- PostgreSQL healthcheck (`pg_isready`) added to `docker-compose.yml` with `condition: service_healthy` for backend startup ordering
- updated deployment script to use the production overlay explicitly
- added backup helper script for PostgreSQL dumps and MinIO archive snapshots
- documented the VPS-oriented startup path in the README
- TLS certificate obtained and applied (ssl.conf with doc-ai-assist.com)
- `.env.production.example` expanded with all required variables
- Backend Dockerfile updated to include `alembic.ini` and `alembic/` directory
- Alembic migrations run automatically on deploy

## Docker hardening

### Multi-stage frontend build

The frontend Dockerfile uses a three-stage build:
1. **dev** stage: runs `vite dev` for local development
2. **build** stage: runs `npm run build` to produce static assets
3. **production** stage: copies built assets into an `nginx:1.27-alpine` image with a custom `nginx.conf` serving on port 5173 with SPA fallback and cache headers

`docker-compose.yml` targets the `dev` stage; `docker-compose.prod.yml` targets `production` with `VITE_API_BASE_URL` build arg.

### Non-root backend container

The backend Dockerfile creates a dedicated `appuser` and switches to it before running the application. This limits the blast radius of potential container escapes.

### .dockerignore files

- `backend/.dockerignore`: excludes `__pycache__`, `.env`, `.git` (scripts and tests are included for in-container usage)
- `frontend/.dockerignore`: excludes `node_modules`, `dist`, `.git`, `*.md`

### Environment management

- `.env.production.example` provides a production-ready template with placeholder values
- Startup validation in `config.py` rejects the default `SECRET_KEY` outside development
- `OPENAI_API_KEY` defaults to empty so fallback AI mode is active out of the box
- `.gitignore` preserves both `.env.example` and `.env.production.example`

### Port exposure strategy

- `docker-compose.yml` (dev): backend port 8000 exposed; all frontend API calls use relative `/api/v1` through the Nginx proxy
- `docker-compose.prod.yml`: backend port overridden to `[]` so only Nginx is publicly accessible

### Nginx proxy configuration

- `default.conf`: security headers (X-Content-Type-Options, X-Frame-Options, X-XSS-Protection, Referrer-Policy), gzip compression, proxy buffer tuning, WebSocket proxy for Vite HMR
- `ssl.conf`: TLS template with HSTS, same proxy locations and WebSocket support as default.conf

## Operational notes

- the database and storage services remain private to the Docker network in production
- only the reverse proxy should be exposed publicly
- backups are handled through a lightweight script that can later be scheduled with cron

## Current limitations

- backup creation exists, but there is still no scheduled off-site copy or documented restore drill
- the deploy health check currently targets `http://localhost/health`, which is sufficient for a basic smoke test but not as strict as an HTTPS readiness check through the production proxy

## Verification — COMPLETED 2026-03-11

- VPS deployed successfully with `bash infrastructure/scripts/deploy.sh`
- Alembic migration ran: `INFO [alembic.runtime.migration] Will assume transactional DDL.`
- Health check passed: `OK: Backend healthy after 2 attempt(s).`
- TLS certificate issued by Let's Encrypt for doc-ai-assist.com
- All 5 containers healthy: proxy, frontend, backend, postgres, minio
- https://doc-ai-assist.com loads frontend, /docs loads Swagger UI, /health returns ok

## Next step

Tighten operational evidence for submission: capture screenshots, document a restore test for backups, and harden the deploy smoke test.
