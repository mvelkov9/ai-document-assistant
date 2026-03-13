# Runtime Validation Note

## What was validated directly

- Python backend source compiles successfully (34 files, 0 failures).
- Python tests compile successfully.
- Seed script compiles successfully.
- Docker Compose configuration resolves successfully with the current repository files (both dev-only and dev+prod overlay).
- The user validated that `node -v`, `npm -v`, `docker ps`, and `docker compose version` work in the target shell.
- The user validated that `docker compose build` completes successfully for both backend and frontend images.

## VPS production deployment — VALIDATED 2026-03-11

- VPS: Hetzner CX33, Ubuntu 24.04, IP 178.104.25.28
- Domain: doc-ai-assist.com → A record pointing to VPS IP
- TLS: Let's Encrypt certificate issued, expires 2026-06-09
- Deploy: `bash infrastructure/scripts/deploy.sh` completed successfully
- Alembic migration: executed inside backend container
- Health: `OK: Backend healthy after 2 attempt(s).`
- All 5 containers: proxy (nginx+TLS), frontend (production build), backend, postgres, minio
- https://doc-ai-assist.com — frontend loads, /docs and /redoc accessible, /health returns ok

## Final audit fixes validated

- OPENAI_API_KEY is empty in .env and .env.example (fallback AI mode active by default).
- /redoc proxy location exists in both Nginx configs.
- Backend port 8000 is exposed in dev docker-compose.yml and correctly hidden (ports: []) in production overlay.
- /api/v1/status returns a complete features list matching all implemented capabilities.
- /health and /ready endpoints have OpenAPI summary and description parameters.
- .gitignore preserves both .env.example and .env.production.example.

## Automated test suite

- 111 test cases across 9 test files (87% measured backend coverage)
- Covers: auth validation, document operations, pagination, access control, error handling, async jobs, admin endpoints, document download, Prometheus metrics, AI summary service, storage service, PDF extraction, password hashing, JWT tokens
- Uses mocked storage and AI layers for deterministic execution
- Coverage threshold enforced in CI (≥70%)

## CI pipeline validation

- GitHub Actions workflow runs six jobs: ruff lint + format check, pytest with coverage, prettier check, frontend build, Docker image build, and deploy on `main`
- Pipeline triggers on push to main/master and on pull requests

## Code quality

- `ruff` linter configured via `pyproject.toml` (rules: E, F, I, W; line length 120; known-first-party: app)
- `ruff format` enforces consistent Python code style (double quotes, space indent)
- `prettier` enforces consistent frontend code style (single quotes, no semicolons, trailing commas)
- Structured JSON logging via structlog
- Global exception handlers prevent stack trace leakage

## What is not yet validated end-to-end

- Browser-level screenshot capture of all flows (login, upload, summary, Q&A, admin) — pending for report.

## Practical implication

The repository is deployed and running on the production VPS. All required validation steps have been completed.

## Recommended final steps

1. Capture screenshots of all frontend pages for the academic report.
2. Run `curl -I https://doc-ai-assist.com` to document security headers.
3. Make Michel Velkov admin on VPS database.
4. Finalize the academic report with visual evidence.
