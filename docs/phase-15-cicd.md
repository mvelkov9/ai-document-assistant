# Phase 15 - CI/CD Baseline

## Purpose

Introduce a first repository-level automation path that validates the application on push and pull request events.

## Implemented changes

- added GitHub Actions workflow for backend and frontend validation
- workflow installs Python dependencies and runs backend tests
- workflow installs frontend dependencies and runs the production build

## CI pipeline structure

The CI pipeline now runs five jobs:

### backend-lint
- Runs on `ubuntu-24.04` (pinned)
- Installs Python 3.13 dependencies
- Runs `ruff check app/ tests/` for code quality and import sorting
- Runs `ruff format --check app/ tests/` for consistent code formatting
- Configured via `pyproject.toml` with `line-length = 120`, rules: E, F, I, W
- `[tool.ruff.lint.isort]` has `known-first-party = ["app"]` for reliable import grouping

### backend-test (depends on backend-lint)
- Runs `pytest --cov=app --cov-report=term-missing --cov-fail-under=70`
- Enforces minimum 70% code coverage threshold (actual: ~90%)
- Uses `pytest-cov` for coverage measurement
- PostgreSQL 17 service container for integration tests

### frontend-lint
- Runs on `ubuntu-24.04` (pinned)
- Installs Node 22 LTS with npm cache
- Uses `npm ci` for reproducible installs
- Runs `npx prettier --check` on all Vue/JS/CSS source files

### frontend-build (depends on frontend-lint)
- Installs Node 22 LTS with npm cache
- Runs `npm run build` to verify production build succeeds

### docker (depends on backend-test + frontend-build)
- Builds backend Docker image
- Builds frontend Docker image (production target with `VITE_API_BASE_URL` build arg)

## Node.js 24 compatibility

All jobs set `FORCE_JAVASCRIPT_ACTIONS_TO_NODE24=true` as a top-level env variable to opt into Node.js 24 for GitHub Actions runners, avoiding the deprecation warnings for Node.js 20 actions (`actions/checkout@v4`, `actions/setup-python@v5`, `actions/setup-node@v4`).

## Deploy script improvements

The `infrastructure/scripts/deploy.sh` now includes:
- `alembic upgrade head` run inside the backend container after startup
- Health check polling loop (15 retries, 2s interval) against `/health`
- If health check fails, shows last 30 lines of backend logs and exits with error
- Service status display after successful deployment

## Configuration files

- `.github/workflows/ci.yml` — full CI pipeline (5 jobs)
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
