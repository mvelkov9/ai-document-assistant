# Phase 03 - Infrastructure Strategy

## Purpose

Select a practical infrastructure strategy that minimizes extra cost while still satisfying the hosting requirement of the assignment.

## Selected deployment model

The primary deployment target is a personal VPS running Docker Compose. This gives a valid cloud-hosted solution without forcing dependence on multiple paid managed platforms.

## Planned infrastructure components

- Linux VPS
- Docker Engine and Compose plugin
- Nginx reverse proxy
- frontend container
- backend container
- PostgreSQL container
- MinIO container
- named volumes for persistent storage

## Why VPS was selected

- lower recurring cost if a VPS already exists
- higher architectural control for the report
- easier explanation of network, TLS, storage, and deployment choices
- simpler mapping between local Docker and production Docker

## Evaluator onboarding goal

The evaluator should be able to run the project locally with a minimal command path and inspect a hosted VPS deployment without manual system setup.

## Planned operational controls

- `.env`-driven configuration
- reverse proxy in front of application services
- health endpoint for quick validation
- separate persistent volumes for database and object storage
- future backup scripts for critical data

## Risks and mitigations

### Operational burden

Risk: a VPS adds responsibility for updates and TLS.

Mitigation: keep the stack small and document deployment steps carefully.

### Runtime mismatch

Risk: local and VPS setups diverge.

Mitigation: use Docker Compose in both environments as much as possible.

### AI cost variability

Risk: AI usage can become the largest running cost.

Mitigation: limit document size, rate-limit requests later, and keep the adapter swappable.

## Verification

- hosting requirement is covered by a real cloud-hosted VPS target
- the chosen model still allows professor-friendly local reproduction

## Next step

Create the repository skeleton and the initial application scaffolding.
