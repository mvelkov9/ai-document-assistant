# Phase 02 - Architecture and Data Flows

## Purpose

Define the first architectural baseline for the application, its main components, and the most important data flows.

## Logical architecture

The system is currently designed as a modular monolith with external integrations:

- Vue frontend for user interaction
- FastAPI backend for REST API and orchestration
- PostgreSQL for metadata and application state
- MinIO as S3-compatible object storage for PDF files
- AI provider adapter for summary and Q&A generation
- optional background worker for long-running processing

## Deployment architecture

The production deployment will target one VPS with Docker Compose:

- Nginx reverse proxy exposed to the internet
- frontend container
- backend container
- PostgreSQL container
- MinIO container
- optional worker container in later phases

## Main data flows

### Login flow

1. user submits credentials from frontend
2. backend validates identity and issues token
3. frontend stores token and calls protected endpoints

### Document upload flow

1. user uploads PDF from frontend
2. backend validates type and size
3. file is stored in object storage
4. metadata is saved in PostgreSQL
5. processing job is marked for summary generation

### Summary flow

1. frontend requests summary generation
2. backend loads document metadata and content reference
3. backend calls AI adapter
4. summary is stored and returned to the user

### Question-answer flow

1. user submits a question for a selected document
2. backend resolves document ownership and authorization
3. AI adapter generates answer based on document context
4. answer is stored for traceability and displayed in UI

## Architectural decisions

- prefer one backend service first over microservices
- abstract AI integration behind an adapter for future provider changes
- keep storage external to database for realistic cloud architecture
- keep production close to local setup by using Docker Compose in both environments

## Security impact

- protected document access must be ownership-aware
- object storage should not be public
- API secrets must stay in environment configuration
- reverse proxy will handle TLS in production

## Open questions (resolved)

- ~~whether to store extracted text in PostgreSQL or temporary cache~~ — resolved: text is extracted on-the-fly from MinIO PDFs, not stored separately
- ~~whether the first async implementation should be background tasks or a separate worker~~ — resolved: background tasks in the application process (Phase 12)
- ~~whether authentication should start with local JWT only or immediately include refresh tokens~~ — resolved: local JWT only (Phase 05/06); refresh tokens remain a known limitation

## Verification

- architecture satisfies the integration requirement
- architecture supports cost analysis and threat modeling
- architecture is feasible on a single VPS

## Next step

Materialize the architecture into folder structure, runtime definitions, and starter services.
