# Phase 18: Costs and Organizational Fit

## Goal

Document the financial, operational, and architectural consequences of the selected VPS-based deployment model and compare it with a more managed alternative.

## What was added in this phase

- formalized three cost scenarios for the solution lifecycle
- summarized the main cost drivers: VPS, storage growth, backups, and AI usage
- documented why a personal VPS is an acceptable deployment target for the assignment
- recorded the main tradeoffs between the selected stack and a managed PaaS approach
- aligned the report and master plan with the current operational readiness of the repository

## Cost view

### Concrete cost table

| Item | Demo / exam run | Small organization | Notes |
| --- | --- | --- | --- |
| VPS (Hetzner CX22, 2 vCPU, 4 GB RAM) | €3.65/month | €3.65/month | All containers on one server |
| Domain (.com — Namecheap) | ~$10/year (~€0.75/month) | ~$10/year | doc-ai-assist.com |
| TLS certificate (Let's Encrypt) | free | free | Automated renewal (certbot timer) |
| Object storage (MinIO on VPS) | included in VPS | included in VPS | Up to ~40 GB on CX22 disk |
| AI API (Groq free tier; OpenAI/Gemini fallback) | €0/month | €0–15/month | Groq free; OpenAI ~€0.002/1K tokens if fallback used |
| Database (PostgreSQL on VPS) | included in VPS | included in VPS | Docker container |
| Prometheus metrics | included in VPS | included in VPS | /metrics endpoint |
| **Monthly total** | **~€4–5** | **~€4–20** | |

### VPS vs. Managed PaaS comparison

| Item | VPS approach | Managed PaaS (AWS/GCP equivalent) |
| --- | --- | --- |
| Compute | €3.65/month (Hetzner CX22) | €15–40/month (App Platform, Cloud Run) |
| Database | included (Docker PostgreSQL) | €10–25/month (managed DB) |
| Object storage | included (MinIO) | €1–5/month (S3) |
| AI API | €0 (Groq free tier) | €0–15/month (OpenAI / Groq paid) |
| **Total** | **~€4–5/month** | **€30–85/month** |

Managed PaaS simplifies operations but costs 3–5× more for comparable scope.

### Low-cost demo scenario

- one VPS instance hosts Nginx, frontend, backend, PostgreSQL, and MinIO
- fallback AI mode can be used to avoid mandatory external AI charges
- operational complexity stays moderate because the stack is deployed with Docker Compose

### Small organization scenario

- the same architecture remains valid, but storage and backup volume increase over time
- AI usage becomes the first variable cost that can grow noticeably with user adoption
- periodic maintenance of the VPS, backups, and secrets becomes part of normal operations

### Growth scenario

- AI processing becomes the dominant variable expense
- background processing should be separated into a dedicated worker when load increases
- additional observability and stricter backup monitoring become necessary

## Organizational fit

The chosen architecture is a strong fit for a smaller Slovenian organization that wants predictable fixed costs, direct control over data placement, and a deployable internal service without immediate dependence on several paid managed platforms.

The model is less suitable for teams that have no operational ownership, require strict managed compliance controls from day one, or expect rapid high-volume scaling without adding worker and observability layers.

## Comparison with managed PaaS

### Advantages of the selected VPS model

- lower fixed monthly cost in the assignment scope
- easier cost explanation in the written report
- full control over reverse proxy, storage, and deployment layout
- high similarity between local Docker setup and production deployment

### Advantages of a managed platform alternative

- less system administration work
- easier TLS, metrics, and autoscaling integration
- lower operational risk for teams without infrastructure experience

## Validation note

The latest repository state is aligned with the user's confirmed shell environment, where Docker Compose builds for backend and frontend succeed. The remaining validation work is not a buildability issue but an end-to-end runtime verification step.

## Remaining improvements

1. measure storage growth on seeded and real documents
2. capture real deployment evidence from the VPS for the final defense package
3. monitor actual AI API usage to validate cost estimates