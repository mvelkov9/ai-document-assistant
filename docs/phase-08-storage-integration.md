# Phase 08 - Storage Integration

## Purpose

Implement the first end-to-end business workflow that demonstrates integration between the authenticated backend, relational metadata storage, and S3-compatible object storage.

## Implemented changes

- added document schemas for upload response, listing, and detail retrieval
- added document repository for metadata persistence and ownership filtering
- added MinIO storage service with lazy bucket creation
- added authenticated endpoints for upload, listing, and document detail
- added PDF validation for filename, content type, and maximum size

## API endpoints in this phase

- `POST /api/v1/documents/upload`
- `GET /api/v1/documents`
- `GET /api/v1/documents/{document_id}`
- `DELETE /api/v1/documents/{document_id}` *(added in v1.1.1)*

## Integration path

1. authenticated user sends a PDF upload request
2. backend validates content type and file size
3. backend stores the file into MinIO using a generated storage key
4. backend writes metadata into the relational database
5. frontend or API client can list only that user's uploaded documents

## Pagination

The document listing endpoint now supports pagination:

- `GET /api/v1/documents?skip=0&limit=20` with configurable offset and page size
- Server caps maximum limit at 100
- Response includes `total`, `skip`, and `limit` fields in `DocumentListResponse`
- Repository layer supports `skip/limit` parameters and a separate `count_for_owner` method

## Current limitations

- upload supports only PDF in this iteration
- storage availability errors are returned as API failures and are not yet retried

## Security notes

- document routes require bearer authentication
- metadata listing is owner-scoped
- object storage is meant to remain private behind application access control
- upload size is bounded by configuration

## Verification

- Python source compilation completed after the upload refactor
- editor diagnostics reported no immediate file errors

## Next step

Add extraction and AI summary processing on top of stored document references.
