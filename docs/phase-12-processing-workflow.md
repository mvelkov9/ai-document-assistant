# Phase 12 - Processing Workflow

## Purpose

Introduce asynchronous processing for expensive document operations so the API and frontend do not have to block on long-running summary generation or document question answering.

## Implemented changes

- added persistent processing job model
- added job repository and polling schema
- added async summary job creation endpoint
- added async question job creation endpoint
- added background task runner for summary execution
- added background task runner for question execution
- added job status polling endpoint
- extended job records with input and result payload fields
- updated frontend summary action to poll for completion and refresh the document list
- updated frontend question action to use async jobs and polling
- refined document processing states to distinguish summary and question execution failures

## Why this matters

Summary generation and question answering can become slow or bursty. Persisted jobs give the application a more realistic cloud-service shape and reduce coupling between the request-response cycle and expensive processing.

## Current behavior

1. user triggers summarize or ask on a document
2. frontend or API client creates a processing job
3. backend responds immediately with a queued job record
4. background processing runs on the server
5. client polls job status until it is completed or failed
6. on success, the client reads the generated summary or answer from the job result or refreshed document data

## Session management

Background task runners create dedicated database sessions with proper lifecycle management:

- Repository and service instances are created inside a try block with the dedicated session
- `try/except/finally` ensures the session is always closed, even on failure
- Job status is marked as `running` before processing and `completed` or `failed` after
- A failed job re-fetches its record before marking failure to avoid stale state issues

## Current limitations

- background execution uses the application process and is not yet a separate worker service
- job retries are not implemented yet

## Verification

- editor diagnostics reported no immediate file errors after extending async polling to document questions
- ~~shell-based test execution is currently blocked on this machine because `pytest` is not available on `PATH`~~ — resolved: 39 tests passing via `docker compose exec backend python -m pytest`
- editor diagnostics reported no immediate file errors

## Next step

Move processing into a dedicated worker if needed and split document processing state into separate summary and question dimensions when migrations are introduced.
