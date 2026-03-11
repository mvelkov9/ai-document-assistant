# Phase 17 - Testing

## Purpose

Strengthen the project with repeatable automated checks for backend user flows, error handling, access control, and input validation.

## Implemented changes

- kept and extended health and auth tests
- added dedicated test files for auth edge cases and document operations
- added shared test fixtures in conftest.py for common patterns
- added `pytest-cov` for coverage measurement
- mocked storage and AI-dependent parts so tests stay deterministic

## Test files and counts

| File | Tests | Coverage |
| --- | --- | --- |
| `test_health.py` | 5 | Health, status, readiness, auth flow, duplicate registration |
| `test_document_flow.py` | 6 | Upload, summarize, Q&A, async jobs, job status |
| `test_auth.py` | 8 | Short password, invalid email, missing fields, wrong password, nonexistent user, no token, invalid token, duplicate email |
| `test_documents.py` | 11 | Non-PDF upload, no auth upload, 404 document, cross-user access, pagination, empty list, limit cap, 404 summarize, short question, long question, 404 job |
| `test_admin_and_download.py` | 9 | Admin stats, admin users, 403 regular user, 401 unauthorized, document download (happy/404/cross-user), Prometheus metrics |
| **Total** | **39** | |

## Shared fixtures (conftest.py)

- `test_environment` (autouse) — sets SQLite test DB and env vars; sets `APP_ENV=test` to disable rate limiting
- `client` — FastAPI TestClient with settings cache management; drops all tables and re-initializes DB between tests for isolation
- `mock_storage` — patches MinIO upload/download to no-ops
- `mock_ai` — patches PDF extraction and AI summary/Q&A
- `mock_background_jobs` — patches async job runners to no-ops
- `auth_headers` — registers a user and returns bearer token headers
- `upload_document` — uploads a sample PDF and returns document JSON
- `_register_and_login()` — helper function for multi-user test scenarios

### Test environment configuration

- Rate limiting is disabled via `APP_ENV=test` (set at module level before app imports)
- SQLite is used as the database for test isolation
- Database state is cleaned between tests with `Base.metadata.drop_all()` + `init_db()`

## Covered scenarios

1. Health and readiness endpoints
2. User registration and login (happy path)
3. Duplicate registration rejection (409)
4. Invalid credentials (401)
5. Invalid/missing token (401/403)
6. Input validation errors (422)
7. PDF upload with mocked storage
8. Non-PDF upload rejection (400)
9. Cross-user document access denial (404)
10. Document pagination with skip/limit
11. Summary and Q&A generation
12. Async job creation and status polling
13. Question length validation (too short, too long)
14. Nonexistent document/job (404)

## CI integration

Tests run in CI with:
```bash
pytest --cov=app --cov-report=term-missing --cov-fail-under=50
```

**Update (v1.2.0):** Test suite expanded to 39 tests across 5 files. Added `test_admin_and_download.py` with 9 tests covering admin stats/users (admin role, 403 for regular users, 401 unauthorized), document download (happy/404/cross-user), and Prometheus metrics endpoint.

## Current limitations

- no end-to-end browser automation
- no container-based integration tests with live MinIO and PostgreSQL in CI
- no load or security-specific test automation

## Next step

Extend toward container-based integration tests and optional frontend component tests.
