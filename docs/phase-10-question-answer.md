# Phase 10 - Document Question-Answer

## Purpose

Extend the document workflow from passive summary generation into an interactive question-answer feature over one selected document.

## Implemented changes

- added persistent question-answer model linked to a document
- added repository methods for saving and listing question-answer records
- added backend service method for asking a question over one stored document
- reused extracted PDF text and provider-or-fallback AI logic
- added authenticated ask endpoint
- extended the Vue dashboard with per-document question input and answer display

## Question-answer flow

1. authenticated user uploads a document
2. user optionally generates a summary
3. user enters a question on one document card
4. backend downloads the file from MinIO and extracts machine-readable text
5. backend answers through external AI mode or a local fallback heuristic
6. answer is stored in the relational database and returned to the frontend

## Why persistence was added

The application should not treat Q&A only as a transient UI action. Persisting the interaction improves traceability, future reporting, and the academic argument for integration depth.

## Security and validation

- Question text must be between 3 and 500 characters (Pydantic schema validation)
- Rate limiting enforced at 10 requests per minute on ask and ask-jobs endpoints
- Only the document owner can ask questions about their documents
- Both synchronous and asynchronous Q&A paths are available

## Current limitations

- only the latest answer is shown directly in the current UI card
- no multi-turn conversation memory exists yet
- OCR is still out of scope, so image-only PDFs remain limited

## Verification

- Python source compilation completed after Q&A integration
- editor diagnostics reported no immediate file errors

## Next step

Move summary and Q&A processing into asynchronous jobs and expose richer processing states to the frontend.
