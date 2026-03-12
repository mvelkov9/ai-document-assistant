# AI Document Assistant — v1.3.1

AI Document Assistant is a semester project for the course *Integracija spletnih strani in servisi* (2025/26, ALMA MATER EUROPAEA). The solution targets **MOŽNOST 3 — Razvoj integrirane spletne storitve** and implements a multi-user web service for secure PDF upload, AI summarization, and document question-answering.

## Architecture Overview

```
┌──────────┐     ┌───────────┐     ┌──────────────┐     ┌────────────┐
│  Vue 3   │────▶│   Nginx   │────▶│   FastAPI    │────▶│ PostgreSQL │
│ Frontend │     │  Reverse  │     │   Backend    │     │   (DB)     │
└──────────┘     │  Proxy    │     └──────┬───────┘     └────────────┘
                 └───────────┘            │
                                    ┌─────┴──────┐
                                    │   MinIO     │     ┌────────────┐
                                    │  (S3-compat)│     │  Groq /    │
                                    └─────────────┘     │  Gemini /  │
                                                        │  OpenAI    │
                                                        └────────────┘
```

| Layer | Technology |
|-------|-----------|
| Frontend | Vue 3.5 + Vite 5 + Vue Router 4, Inter font, sidebar layout with admin panel |
| Backend | Python 3.13, FastAPI 0.116, SQLAlchemy 2.0, Alembic |
| Database | PostgreSQL 17 |
| Object storage | MinIO (S3-compatible) |
| AI | Groq (free, Llama 4 Scout 17B-16E), Gemini, or OpenAI — with automatic fallback |
| Reverse proxy | Nginx 1.27 with security headers, WebSocket proxy for Vite HMR |
| Containerization | Docker Compose with PostgreSQL healthcheck (dev + prod overlay) |
| CI/CD | GitHub Actions (lint, test, coverage, build, deploy) |
| Monitoring | Prometheus + Grafana dashboards |

## Quick Start

### Prerequisites
- Docker & Docker Compose
- (Optional) Node 22, Python 3.13 for local dev

### Full Stack (Docker)

```bash
cp .env.example .env          # Edit with your values
docker compose up --build      # Development mode
```

Services available:
- **Frontend**: http://localhost
- **API docs**: http://localhost/docs
- **Health**: http://localhost/health

### Production Deployment

```bash
cp .env.production.example .env   # Fill in production values
bash infrastructure/scripts/deploy.sh
```

### Local Backend (without Docker)

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check |
| `GET` | `/ready` | Readiness (DB + MinIO) |
| `GET` | `/metrics` | Prometheus metrics |
| `GET` | `/api/v1/status` | Service info |
| `POST` | `/api/v1/auth/register` | Register user |
| `POST` | `/api/v1/auth/login` | Login, get JWT |
| `GET` | `/api/v1/auth/me` | Current user profile |
| `POST` | `/api/v1/documents/upload` | Upload PDF |
| `GET` | `/api/v1/documents` | List documents (paginated) |
| `GET` | `/api/v1/documents/{id}` | Get document |
| `GET` | `/api/v1/documents/{id}/download` | Download PDF |
| `POST` | `/api/v1/documents/{id}/summarize` | Summarize (sync) |
| `POST` | `/api/v1/documents/{id}/summarize-jobs` | Summarize (async) |
| `POST` | `/api/v1/documents/{id}/ask` | Q&A (sync) |
| `POST` | `/api/v1/documents/{id}/ask-jobs` | Q&A (async) |
| `DELETE` | `/api/v1/documents/{id}` | Delete document |
| `GET` | `/api/v1/jobs/{id}` | Job status |
| `GET` | `/api/v1/admin/users` | List all users (admin) |
| `GET` | `/api/v1/admin/stats` | System statistics (admin) |
| `PATCH` | `/api/v1/admin/users/{id}/role` | Set user role (admin) |

Interactive documentation: `/docs` (Swagger UI) and `/redoc`.

## Database Migrations

The project uses Alembic for schema migrations:

```bash
cd backend
alembic upgrade head          # Apply latest migrations
alembic revision --autogenerate -m "description"   # Generate new migration
```

In production, the deploy script runs `alembic upgrade head` automatically.

## Security

- **Authentication**: JWT bearer tokens (HS256, python-jose)
- **Password hashing**: bcrypt 4.0.1 via passlib (pinned for Python 3.13 compatibility)
- **Rate limiting**: slowapi — 5/min on auth, 10/min on AI endpoints (disabled in test environment)
- **Input validation**: Pydantic schemas with length constraints
- **Security headers**: X-Content-Type-Options, X-Frame-Options, X-XSS-Protection, Referrer-Policy via Nginx
- **Non-root containers**: Backend runs as `appuser`
- **CORS**: Restricted to specific methods and headers
- **Startup validation**: Rejects default `SECRET_KEY` in production

**Known limitation**: JWT tokens stored in localStorage (documented trade-off vs httpOnly cookies for SPA).

## Testing

```bash
cd backend
pytest                                         # Run all tests
pytest --cov=app --cov-report=term-missing     # With coverage
```

Test suite covers: auth validation, upload constraints, document access control, pagination, Q&A validation, async jobs, health endpoints, admin endpoints, document download, Prometheus metrics, AI summary service, storage operations, PDF extraction, password hashing, JWT tokens. 107 test cases across 9 test files (~90% code coverage).

Rate limiting is automatically disabled when `APP_ENV=test` to prevent cascade failures.

## CI/CD

GitHub Actions pipeline (`.github/workflows/ci.yml`):
1. **Lint** — `ruff check` + `ruff format --check` on backend code
2. **Test** — `pytest` with coverage (≥70% threshold)
3. **Frontend lint** — `prettier --check`
4. **Frontend build** — `npm run build`
5. **Docker** — Build backend and frontend images
6. **Deploy** — SSH to VPS and run `deploy.sh` (main branch only)

## Monitoring

Prometheus scrapes FastAPI `/metrics` every 15 s. Grafana is pre-provisioned with a dashboard showing request rate, p50/p95 latency, error rate, and in-progress requests.

- **Dev**: Grafana at http://localhost:3000, Prometheus at http://localhost:9090
- **Prod**: Ports closed, access via SSH tunnel or Nginx location

## Demo Seed

```bash
docker compose exec backend python scripts/seed_demo.py
```

Credentials: `demo.user@example.com` / `VerySecure123`

## Project Structure

```
backend/          FastAPI application, models, services, tests
frontend/         Vue 3 SPA with component-based architecture
infrastructure/   Nginx config, deploy & backup scripts
docs/             Phase documentation (18 phases)
report/           Academic report
```

## Documentation Trail

Implementation is tracked across 18 phase documents in `docs/`, covering scope, architecture, infrastructure, backend API, data storage, storage integration, AI summary, Q&A, frontend flows, processing workflow, OpenAPI, VPS deployment, CI/CD, observability, testing, and cost analysis.

