# Phase 15 - CI/CD Baseline

## Purpose

Introduce a first repository-level automation path that validates the application on push and pull request events.

## Implemented changes

- added GitHub Actions workflow for backend and frontend validation
- workflow installs Python dependencies and runs backend tests
- workflow installs frontend dependencies and runs the production build

## CI pipeline structure

The CI pipeline now runs four jobs:

### backend-lint
- Installs Python 3.13 dependencies
- Runs `ruff check app/ tests/` for code quality and import sorting
- Runs `ruff format --check app/ tests/` for consistent code formatting
- Configured via `pyproject.toml` with `line-length = 120`, rules: E, F, I, W
- `[tool.ruff.lint.isort]` has `known-first-party = ["app"]` for reliable import grouping

### backend-test (depends on backend-lint)
- Runs `pytest --cov=app --cov-report=term-missing --cov-fail-under=50`
- Enforces minimum 50% code coverage threshold
- Uses `pytest-cov` for coverage measurement

### frontend
- Installs Node 22 with npm cache
- Runs `npx prettier --check` on all Vue/JS/CSS source files
- Runs `npm run build` to verify production build

### docker (depends on backend-test + frontend)
- Builds backend Docker image
- Builds frontend Docker image (production target with `VITE_API_BASE_URL` build arg)

## Deploy script improvements

The `infrastructure/scripts/deploy.sh` now includes:
- `alembic upgrade head` run inside the backend container after startup
- Health check polling loop (15 retries, 2s interval) against `/health`
- If health check fails, shows last 30 lines of backend logs and exits with error
- Service status display after successful deployment

## Configuration files

- `.github/workflows/ci.yml` — full CI pipeline (4 jobs)
- `backend/pyproject.toml` — ruff lint, ruff format, isort, and pytest configuration
- `frontend/.prettierrc` — prettier formatting rules for Vue/JS/CSS
- `.env.production.example` — production environment template

## Current limitations

- no automatic VPS deployment is attached yet
- runtime integration tests against live MinIO and PostgreSQL are not part of CI

## Verification

- workflow definition created successfully
- local execution of the workflow is not possible in this environment without Node and Docker tooling

## Next step

Add deployment automation for the VPS and extend validation toward containerized integration checks.
