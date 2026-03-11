# Phase 16 - Observability Baseline

## Purpose

Introduce a minimal but real observability layer so the application is easier to operate and troubleshoot on a VPS.

## Implemented changes

- replaced basic request logging middleware with structured JSON logging via `structlog`
- removed unused `logging` stdlib import from `main.py`
- configured structlog with ISO timestamps, log levels, and JSON rendering
- every HTTP request is logged with method, path, status code, and duration in milliseconds
- added `/ready` endpoint for dependency-aware readiness checks
- expanded backend status reporting to mention readiness and logging features

## Structured logging configuration

The backend uses `structlog` with the following processor pipeline:
1. `merge_contextvars` — allows request-scoped context variables
2. `add_log_level` — includes log level in output
3. `TimeStamper(fmt="iso")` — ISO 8601 timestamps
4. `JSONRenderer` — machine-parseable JSON output

Example log entry:
```json
{"method": "POST", "path": "/api/v1/auth/login", "status": 200, "duration_ms": 45.2, "event": "request", "level": "info", "timestamp": "2026-03-11T10:00:00Z"}
```

## Global exception handlers

Three exception handlers prevent information leakage:

| Exception | HTTP Status | Response |
| --- | --- | --- |
| `RateLimitExceeded` | 429 | `{"detail": "Too many requests. Please try again later."}` |
| `RequestValidationError` | 422 | `{"detail": "Validation error. Check your request parameters."}` |
| Unhandled `Exception` | 500 | `{"detail": "An internal error occurred."}` |

For 500 errors, the actual error message is logged server-side with structlog but never exposed to the client.

## Current readiness scope

- relational database connectivity check
- MinIO bucket accessibility check

## Current limitations

- ~~no metrics endpoint is exposed yet~~ — resolved in v1.2.0: Prometheus `/metrics` endpoint via `prometheus-fastapi-instrumentator`, proxied through Nginx
- no centralized log aggregation is configured yet
- no distributed tracing is implemented yet

## Verification

- Python source compilation completed after observability changes
- editor diagnostics reported no immediate file errors

## Next step

Add production rollout checks, optional uptime monitoring, and later structured export of logs if needed.
