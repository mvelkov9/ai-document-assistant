# Architecture and Data Flows

## Purpose

This document consolidates the main logical architecture, deployment view, and key data flows of the AI Document Assistant solution. It is intended as a direct source for the academic report and as the primary location of the mandatory architectural diagrams.

## Included diagrams

- `docs/diagrams/architecture.mmd` for the logical and deployment architecture
- `docs/diagrams/data-flow.mmd` for the key application data flows

## Logical architecture summary

The system is built as a modular monolith with external integrations:

1. Vue frontend for user interaction (component-based: AuthPanel, UploadSection, DocumentCard)
2. FastAPI backend for API and orchestration with structured JSON logging (structlog)
3. PostgreSQL for users, documents, Q&A records, and processing jobs (managed by Alembic migrations)
4. MinIO for object storage of PDF files
5. AI provider adapter with provider and fallback modes
6. Background-task based async summary and Q&A processing with session lifecycle management
7. Nginx reverse proxy with security headers, gzip, TLS preparation, and `/redoc` + `/docs` proxying
8. slowapi rate limiting on authentication (5/min) and AI endpoints (10/min)

## Deployment summary

The production deployment runs on a Hetzner CX33 VPS (4 vCPU, 8 GB RAM, Ubuntu 24.04) at **https://doc-ai-assist.com** (IP: 178.104.25.28). TLS is provided by Let's Encrypt with automatic renewal. Public traffic enters through Nginx, while backend, database, and object storage remain on the internal Docker network.

### Container details

- **Frontend**: multi-stage build (dev/build/production), production serves static files via nginx:1.27-alpine
- **Backend**: Python 3.13-slim, runs as non-root user (appuser), Alembic migrations on deploy
- **PostgreSQL 17**: persistent volume, internal network only
- **MinIO**: S3-compatible storage, persistent volume, internal network only
- **Nginx**: reverse proxy with security headers, gzip, rate forwarding

### CI/CD

GitHub Actions pipeline: ruff lint + format check → pytest with coverage (min 50%) → prettier check + frontend build → Docker image build. Deploy script runs Alembic migration and health check polling.

## Main flows

### Authentication

User credentials are sent from the frontend to the backend. After validation, the backend returns a JWT access token. The frontend uses this token for all protected operations.

### Upload

The user uploads a PDF through the frontend. The backend validates the file, stores it in MinIO, and records the metadata in PostgreSQL.

### Async summary

The frontend creates a summary job. The backend stores the job, processes it in the background, extracts PDF text, generates a summary via AI provider or fallback logic, and updates both the document and the job state.

### Document question-answer

The user submits a question for a selected document. The backend loads the document content from MinIO, extracts text, generates an answer, stores the result in PostgreSQL, and returns the answer to the frontend.

## Recommendation for report usage

These diagrams should be referenced directly in the report chapter on architecture and in the chapter on integration and data flows.
