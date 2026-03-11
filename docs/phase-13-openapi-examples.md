# Phase 13 - OpenAPI Examples and Demo Seed

## Purpose

Improve API usability for evaluation and development by adding concrete request/response examples and a repeatable seed path for quick demonstration.

## Implemented changes

- added schema-level example payloads for auth, document, question-answer, and processing job models
- added endpoint-level `summary` and `description` parameters to all API routes
- expanded README with a demo seed workflow and credentials
- added backend seed script that creates a demo user and a sample PDF document

## Endpoint documentation

All API endpoints now include:

- `summary`: short action-oriented label visible in Swagger UI sidebar
- `description`: detailed explanation of endpoint behavior, input requirements, and response semantics

This includes the root-level `/health` and `/ready` endpoints as well as all `/api/v1/*` routes.

Both `/docs` (Swagger UI) and `/redoc` (ReDoc) render the full documentation and are accessible through the Nginx reverse proxy.

## Current limitations

- the seed script creates one demo user and one demo document only

## Verification

- seed script file was created successfully
- editor diagnostics reported no immediate file errors in the updated schema files

## Next step

Add richer endpoint-level examples and keep the demo seed path aligned with the final VPS deployment instructions.
