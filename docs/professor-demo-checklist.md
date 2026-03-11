# Professor Demo Checklist

## Purpose

This document is a short, evaluator-friendly checklist for verifying the semester project with minimal setup effort.

## Fast verification path

1. Open a terminal in the project root (`Projektna naloga/`).

2. Copy the example env file (skip if `.env` already exists):

```bash
cp .env.example .env
```

3. Build and start the stack (build one at a time if the VM is low on RAM):

```bash
docker compose build backend
docker compose build frontend
docker compose up -d
```

4. Wait a few seconds for PostgreSQL to become healthy, then verify:

```bash
docker compose ps
```

All 5 containers (proxy, frontend, backend, postgres, minio) should show "Up" or "Healthy".

5. Test the health endpoint:

```bash
curl http://localhost:8000/health
```

Expected: `{"status":"ok","environment":"development"}`

6. Seed demo data (runs **inside** the backend container):

```bash
docker compose exec backend python scripts/seed_demo.py
```

Expected output:
```
Created demo user: demo.user@example.com
Created demo document: demo-company-policy.pdf
```

7. Open in the browser:

| What | URL |
|---|---|
| Application | http://localhost |
| Swagger UI (OpenAPI docs) | http://localhost/docs |
| ReDoc | http://localhost/redoc |
| Health | http://localhost:8000/health |
| Readiness | http://localhost:8000/ready |

8. Log in with the demo account:

- email: `demo.user@example.com`
- password: `VerySecure123`

9. Verify these flows in the browser or via Swagger UI:

- successful login → receive JWT token
- document list → visible seeded PDF document
- summary display or trigger summary generation
- ask a question about the demo document → get an answer

10. Stop when done:

```bash
docker compose down
```

## Expected evidence during demo

- OpenAPI documentation shows auth, documents, jobs, and health endpoints with descriptions
- Both `/docs` (Swagger UI) and `/redoc` (ReDoc) render full API documentation
- document list is user-scoped and paginated
- summary flow changes processing status
- question-answer flow returns a persisted answer
- rate limiting returns 429 on excessive requests
- security headers visible in HTTP responses (`curl -I http://localhost`)
- deployment scripts and backup script are present in `infrastructure/scripts`
- 30 automated backend tests pass:
  ```bash
  docker compose exec backend python -m pytest tests/ -v
  ```
- CI pipeline runs lint, test, and build steps

## Quick curl test commands

```bash
# Health check
curl http://localhost:8000/health

# Readiness check
curl http://localhost:8000/ready

# Register a new user
curl -X POST http://localhost/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"TestPass123","full_name":"Test"}'

# Login and get token
TOKEN=$(curl -s -X POST http://localhost/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"demo.user@example.com","password":"VerySecure123"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
echo $TOKEN

# List documents (authenticated)
curl http://localhost/api/v1/documents/ -H "Authorization: Bearer $TOKEN"

# Check security headers
curl -I http://localhost
```

## Troubleshooting

- **"address already in use" on port 5432**: A local PostgreSQL is running. Either stop it (`sudo systemctl stop postgresql`) or change `POSTGRES_PORT` in `.env` to 5433.
- **Backend exits immediately**: PostgreSQL wasn't ready in time. Run `docker compose restart backend`.
- **Docker "socket permission" error**: Run `sudo usermod -aG docker $USER` and log out/in.
- **VM crashes during build**: Build one image at a time instead of all at once (see step 3).
- **Readiness endpoint fails**: Check that postgres and minio containers are healthy: `docker compose ps`.
