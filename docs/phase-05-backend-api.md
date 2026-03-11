# Phase 05 - Backend API Core

## Purpose

Move the backend from a pure scaffold to a first usable API slice by adding application configuration, initial auth contracts, and a minimal service layer.

## Implemented changes

- kept FastAPI application bootstrapping and CORS configuration
- kept health and status endpoints
- added auth schemas for registration, login, token response, and public user profile
- added security helper module for password hashing and JWT creation
- replaced in-memory auth service with SQLAlchemy-backed persistence
- added register, login, and current-user endpoints
- added backend tests for the auth flow
- added database session dependency and startup initialization

## API endpoints in this phase

- `GET /health`
- `GET /api/v1/status`
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`

## Persistence status

The backend now stores users in a real database layer through SQLAlchemy. This is still an early persistence phase because migrations, richer authorization rules, and document-storage integration are not finished yet.

## Security notes

- passwords are hashed with bcrypt 4.0.1 (pinned for passlib compatibility on Python 3.13), not stored in plain text
- tokens are signed with HS256 using a secret key from configuration
- protected endpoint access requires a bearer token
- rate limiting enforced on auth endpoints (5 requests/minute via slowapi); automatically disabled when `APP_ENV=test`
- CORS restricted to specific methods (GET, POST, OPTIONS) and headers (Authorization, Content-Type)
- startup validation rejects default SECRET_KEY in non-development environments
- global exception handlers prevent stack trace leakage in API responses

## Tests and verification

- backend Python modules compile successfully
- auth endpoints are covered by starter API tests
- full test execution will require installing dependencies from `requirements.txt`

## Enhancement updates

- rate limiting (5/min) added to register and login endpoints via slowapi
- CORS tightened from wildcard to explicit methods and headers
- startup validation added for SECRET_KEY in production
- structured JSON logging with structlog replaced basic request logging
- global exception handlers added for validation errors (422), rate limits (429), and unhandled exceptions (500)
- all endpoints now have OpenAPI summary and description parameters

## Open gaps

- refresh token flow is not yet implemented (known limitation, documented trade-off)
- ~~role-aware authorization policies are not yet enforced beyond basic identity handling~~ — resolved in v1.2.0: admin middleware (`require_admin`), `GET /admin/users`, `GET /admin/stats`, `PATCH /admin/users/{id}/role` added

## Next step

Build the document upload contract and connect file metadata to object storage.
