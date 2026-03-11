# Phase 04 - Repository and Scaffold

## Purpose

Create the initial repository layout, the first code scaffold, and the living documentation structure required for the rest of the project.

## Implemented changes

- created `backend/` base structure for FastAPI
- created `frontend/` base structure for Vue
- created `infrastructure/` for Docker and reverse proxy assets
- created `docs/` master and phase files
- added project `README.md`
- added `.env.example`
- added `.gitignore`

## Folder structure

```text
Projektna naloga/
├── backend/
├── docs/
├── frontend/
├── infrastructure/
└── report/
```

## Why this structure

- separates runtime concerns clearly
- supports academic documentation and implementation in parallel
- makes future CI/CD and VPS deployment easier

## Initial runtime status

- backend scaffold is immediately actionable because Python exists on the machine
- frontend scaffold is prepared but cannot be executed until Node.js is installed
- Docker scaffold is prepared but cannot be executed until Docker is installed

## Validation limits in this phase

- ~~full container validation was not possible because Docker was unavailable~~ — resolved: Docker confirmed available, `docker compose build` succeeds
- ~~frontend build validation was not possible because Node.js and npm were unavailable~~ — resolved: Node.js and npm confirmed available, frontend builds successfully

## Verification performed

- Python 3 detected successfully
- repository structure created successfully
- documentation files created successfully

## Next step

Implement the backend API core with configuration, status routes, and the first domain contracts.
