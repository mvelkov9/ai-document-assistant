# Phase 07 - Data and Storage Baseline

## Purpose

Introduce the first durable persistence layer for the application and prepare the model needed for upcoming document upload and processing flows.

## Implemented changes

- added SQLAlchemy engine and session management
- added declarative base and startup table initialization
- added persistent `User` model
- added initial `Document` metadata model
- created repository-backed auth service using the database session
- prepared a local-friendly default database path while keeping PostgreSQL in `.env.example` for Docker and VPS environments

## Why this phase matters

The previous backend iteration proved the auth API contract. This phase turns that contract into a persistent backend foundation so document workflows do not need another auth rewrite later.

## Current data model

### User

- id
- email
- full_name
- role
- password_hash
- created_at

### Document

- id
- owner_id
- original_filename
- storage_key
- content_type
- size_bytes
- processing_status
- summary_text
- created_at

## Storage strategy

- metadata remains in the relational database
- actual PDF files are stored in MinIO (implemented in Phase 08)
- `storage_key` already exists in the document model so upload implementation can plug into it directly

## Local and production compatibility

- local non-Docker fallback can use SQLite by default for easier development
- Docker and VPS environments stay aligned with PostgreSQL through `.env`
- the domain model is written to remain PostgreSQL-compatible

## Migration strategy

Alembic has been integrated for database schema management:

- `alembic.ini` configured in the backend root
- `alembic/env.py` imports all models and reads `DATABASE_URL` from environment
- Initial migration (`001_initial.py`) creates all 4 tables: users, documents, processing_jobs, question_answers
- Production deployments run `alembic upgrade head` via the deploy script
- `create_all()` is retained for development convenience with a docstring noting Alembic preference

### Files added

- `backend/alembic.ini`
- `backend/alembic/env.py`
- `backend/alembic/script.py.mako`
- `backend/alembic/versions/001_initial.py`

## Risks and open points

- ~~object storage integration is not active yet~~ — resolved in Phase 08: MinIO integration implemented
- ~~processing statuses exist conceptually but the async job workflow is still pending~~ — resolved in Phase 12: async summary and question jobs with polling
- downgrade path exists in migration but has not been tested in production

## Verification

- Python source compilation completed after the persistence refactor
- editor diagnostics reported no immediate file errors

## Next step

Add document upload endpoints, file validation, and MinIO storage integration.

## Delta after follow-up iteration

- the document metadata model is now actively used by upload endpoints
- MinIO integration is implemented in the next phase, keeping this phase as the persistence baseline

