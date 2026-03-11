# Phase 06 - Security Model

## Purpose

Define and implement the application security posture, including authentication hardening, transport security, input validation, rate limiting, and alignment with recognized security frameworks.

## Implemented security measures

### Rate limiting

The application uses `slowapi` to enforce per-IP rate limits on sensitive endpoints:

- Authentication endpoints (register, login): 5 requests per minute per IP
- AI endpoints (summarize, ask, summarize-jobs, ask-jobs): 10 requests per minute per IP
- Exceeded limits return HTTP 429 (Too Many Requests) with a standard JSON error body

### Security headers (Nginx)

The production Nginx reverse proxy adds the following headers to all responses:

- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; connect-src 'self'; img-src 'self' data:;`

Additionally, gzip compression is enabled for text-based content types.

### TLS preparation

A TLS configuration template is available at `infrastructure/nginx/ssl.conf` with Let's Encrypt placeholders. This supports HTTPS deployment with HTTP-to-HTTPS redirect and HSTS headers.

### Input validation

- Password: minimum 8 characters, maximum 128 characters (Pydantic schema)
- Email: validated with `email-validator` library
- Question text: minimum 3, maximum 500 characters
- PDF upload: file extension and MIME type validation, configurable size limit
- Filenames: sanitized with `Path.name` and space replacement

### Credential security

- Passwords hashed with bcrypt (passlib)
- JWT signed with HS256 (python-jose)
- Startup validation rejects default `SECRET_KEY` in non-development environments
- CORS restricted to specific methods (`GET`, `POST`, `OPTIONS`) and headers (`Authorization`, `Content-Type`)

### Container security

- Backend Docker container runs as non-root user (`appuser`)
- `.dockerignore` files exclude sensitive and unnecessary files from build context

### Exception handling

- Global exception handlers prevent stack trace leakage in production responses
- `RequestValidationError` → 422 with generic message
- `RateLimitExceeded` → 429 with rate limit message
- Unhandled `Exception` → 500 with generic message (details logged server-side)

## OWASP Top 10 (2021) alignment

| Category | Measure |
| --- | --- |
| A01 Broken Access Control | Ownership-based document access, bearer token required |
| A02 Cryptographic Failures | bcrypt password hashing, HS256 JWT signing |
| A03 Injection | Pydantic validation, SQLAlchemy ORM (no raw SQL) |
| A04 Insecure Design | Layered architecture (API → Service → Repository) |
| A05 Security Misconfiguration | Startup SECRET_KEY check, security headers, restricted CORS |
| A07 Identification and Authentication Failures | Rate limiting on auth endpoints, password length enforcement |

## Known limitations

- JWT stored in localStorage (XSS risk) — documented trade-off for SPA architecture
- No account lockout after failed login attempts
- No refresh token rotation
- No CSRF protection needed (stateless bearer token auth)

## Verification

- Rate limiting returns 429 after threshold exceeded
- Security headers visible in `curl -I` responses
- Invalid inputs rejected with 422 status
- Default SECRET_KEY rejected on non-development startup

## Files changed or created

- `backend/app/main.py` — rate limiter, exception handlers, CORS config
- `backend/app/api/auth.py` — rate limit decorators
- `backend/app/api/documents.py` — rate limit decorators
- `backend/app/core/config.py` — startup SECRET_KEY validation
- `backend/app/schemas/document.py` — question length constraints
- `backend/app/schemas/auth.py` — password length constraints
- `infrastructure/nginx/default.conf` — security headers, gzip
- `infrastructure/nginx/ssl.conf` — TLS template (new)
- `backend/Dockerfile` — non-root user
- `backend/.dockerignore` — new
- `frontend/.dockerignore` — new

## Next step

Continue hardening with Alembic migrations, structured logging, and expanded test coverage for security-relevant edge cases.
