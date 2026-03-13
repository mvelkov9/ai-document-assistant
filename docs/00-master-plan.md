# Master Implementation Plan

## Project snapshot

- Project title: AI Document Assistant
- Assignment option: MOZNOST 3 - Razvoj integrirane spletne storitve
- Delivery model: local development plus production deployment on a personal VPS
- Main objective: multi-user upload, document storage, AI summarization, basic document Q&A, OpenAPI, CI/CD, and strong documentation

## Course requirement coverage

| Requirement | Status | Notes |
| --- | --- | --- |
| REST API | Completed | FastAPI with 23 endpoints, OpenAPI documentation |
| Cloud integration | Completed | MinIO object storage, Groq / Gemini / OpenAI API, PostgreSQL |
| Cloud hosting | Completed | Docker Compose with production overlay for VPS |
| Basic CI/CD | Completed | GitHub Actions: lint + format (ruff), test (pytest-cov), prettier, build, Docker |
| OpenAPI / Swagger | Completed | Endpoint descriptions, schema examples, /docs + /redoc |
| Authentication | Completed | JWT (HS256), bcrypt passwords, rate-limited auth |
| Multi-user support | Completed | Ownership-based access control on all resources |
| Documentation | Completed | 18 phase docs, academic report, architecture diagrams |

## Phase tracker

| Phase | Title | Status | Main output |
| --- | --- | --- | --- |
| 01 | Scope and scenario | Completed | Project scope, MVP, users, constraints |
| 02 | Architecture and flows | Completed | Initial component and flow design |
| 03 | Infrastructure strategy | Completed | VPS + Docker + Nginx direction |
| 04 | Repository and scaffold | Completed | Initial codebase and documentation structure |
| 05 | Backend API core | Completed | Auth flow, status routes, service contracts |
| 06 | Security model | Completed | Rate limiting, security headers, input validation, OWASP mapping |
| 07 | Data and storage | Completed | SQLAlchemy persistence, Alembic migrations |
| 08 | Storage integration | Completed | Upload endpoint, MinIO service, document listing |
| 09 | AI integration | Completed | Summary endpoint with provider and fallback mode |
| 10 | Document Q&A | Completed | Ask endpoint with persistence and fallback mode |
| 11 | Frontend flows | Completed | Auth, upload, document list, summary UI (componentized) |
| 12 | Processing workflow | Completed | Async summary and question jobs with polling |
| 13 | OpenAPI and examples | Completed | Schema examples, endpoint descriptions, demo seed |
| 14 | Docker profiles | Completed | Multi-stage Dockerfiles, production overlay, non-root |
| 15 | CI/CD | Completed | GitHub Actions: ruff lint, pytest-cov, frontend build |
| 16 | Observability | Completed | Structured JSON logging (structlog), readiness endpoint |
| 17 | Testing | Completed | 111 backend tests, auth/doc/pagination/error coverage |
| 18 | Costs and fit | Completed | Cost tables with real pricing, PaaS comparison |
| 19 | VPS deployment | Completed | Deployed on Hetzner CX33, TLS, doc-ai-assist.com |
| 20 | Frontend expansion | Completed | Search, filter, sort, user profile |
| 21 | Admin functionality | Completed | Admin endpoints, admin dashboard, stats |
| 22 | RAG-lite AI | Completed | BM25 chunking for contextual Q&A |
| 23 | Document download | Completed | Download endpoint + frontend button |
| 24 | Prometheus metrics | Completed | /metrics endpoint with instrumentator |
| 25 | CI/CD health | Completed | Docker build step in CI, badge prep |
| 26 | Report finalization | Completed | Report updated, 16 screenshot placeholders inserted, Word outline ready |
| 27 | GUI overhaul v1.2.1 | Completed | Sidebar layout, admin role management |
| 28 | Hardening v1.2.2 | Completed | PDF extraction fallback, VPS specs CX33, lint fixes |
| 29 | Formatters v1.2.3 | Completed | Ruff format + prettier auto-formatting, CI format checks |
| 30 | Testing & CI v1.2.4 | Completed | 111 tests (87% coverage), CI evolved into 6 jobs including deploy, Node 24 compat |
| 31 | Vue Router v1.3.0 | Completed | Vue Router 4, page splitting (5 routes), composable store, nav guards |
| 32 | Continuous Deployment | Completed | SSH deploy step in GitHub Actions after CI, main branch only |
| 33 | Grafana dashboard | Completed | Prometheus + Grafana containers, pre-provisioned FastAPI dashboard |
| 34 | Backup encryption | Completed | GPG AES-256 encryption, 7-day rotation, verification step |
| 35 | UX & persistence v1.3.2 | Completed | Favicon, last-login tracking, Q&A history persistence, collapsible cards, sidebar tool links |
| 36 | Frontend UX v1.4.0 | Completed | Dark mode, stats dashboard, copy summary, AI loading animations |
| 37 | OCR support v1.4.1 | Completed | PyMuPDF + Tesseract OCR for scanned/image-based PDFs, 3-tier extraction (PyMuPDF → pypdf → OCR), Slovenian language pack |
| 38 | PDF Viewer v1.5.0 | Completed | PdfViewer.vue with pdfjs-dist, page nav, zoom, keyboard shortcuts |
| 39 | Chat Q&A v1.5.0 | Completed | ChatQA.vue with chat bubbles, typing indicator, marked markdown |
| 40 | Dashboard Charts v1.5.0 | Completed | vue-chartjs doughnut (status) + bar (timeline) charts |
| 41 | Mobile Responsive v1.5.0 | Completed | Hamburger drawer menu, responsive breakpoints at 860/640/540px |
| 42 | Multi-File Upload v1.5.2 | Completed | Batch upload with per-file progress bars, drag-and-drop multiple PDFs |
| 43 | Document Tags v1.5.2 | Completed | JSON tags column, PATCH /documents/{id}/tags, tag chips, tag filter |
| 44 | Markdown Summaries v1.5.2 | Completed | AI prompts request structured markdown, rendered with marked.js |
| 45 | Onboarding Wizard v1.5.2 | Completed | 4-step wizard overlay, localStorage dismiss, enhanced empty states |
| 46 | v1.5.1 Fixes & Enhancements | Completed | PDF viewer fix, timestamps, clear chat, enriched admin stats, OpenAPI update |
| 47 | v1.5.2 Feature Bundle | Completed | Phases 42-45 implemented, CI lint fixes, version bump |

## Current implementation state

### Completed in this iteration

- repository structure created
- master documentation created
- four phase documents created
- FastAPI starter application created
- initial authentication endpoints created
- SQLAlchemy database integration created
- persistent user and document models created
- MinIO-compatible document upload flow created
- PDF extraction and AI-or-fallback summary flow created
- document question-answer flow created
- Vue auth and dashboard flow created
- async summary and question job flow created
- OpenAPI example payloads added
- Docker Compose skeleton created
- production Docker Compose overlay created
- Nginx reverse proxy starter configuration created
- VPS deploy and backup scripts created
- readiness endpoint and request logging added
- demo seed script created
- environment example prepared
- GitHub Actions CI workflow scaffolded
- backend document flow tests added
- cost and organizational fit analysis documented
- last_login_at tracking added to User model with Alembic migration
- Q&A history endpoint (GET /documents/{id}/answers) added
- frontend Q&A persistence with full answer history (no refresh loss)
- collapsible document cards (auto-collapse 4th+) implemented
- favicon (SVG with app branding) added
- profile page expanded with created_at and last_login_at
- admin sidebar links for API Docs, ReDoc added
- Alembic migration 002_add_last_login_at created
- Dark mode with CSS custom properties and localStorage persistence
- Stats dashboard cards on DocumentsPage (documents, summaries, questions, % processed)
- Copy-to-clipboard button for AI summaries
- Shimmer + pulse loading animations during AI processing
- questionsCount computed property in store
- PyMuPDF added as primary PDF text extractor (better than pypdf for complex fonts/tables)
- Tesseract OCR fallback for scanned/image-based PDFs (slv+eng)
- Pillow for PDF page rendering at 300 DPI before OCR
- 3-tier PDF extraction pipeline: PyMuPDF → pypdf → OCR
- Graceful degradation for corrupted/empty PDFs (no crashes)
- tesseract-ocr + tesseract-ocr-slv installed in Docker image and CI
- **v1.5.0 GUI overhaul:**
  - PdfViewer.vue: in-app PDF rendering with pdfjs-dist (page nav, zoom, Esc close, responsive)
  - ChatQA.vue: chat-bubble Q&A interface (user right, AI left, typing dots, markdown via marked)
  - DocumentCard.vue: integrated PdfViewer + ChatQA, "Preberi" button, removed flat Q&A
  - DocumentsPage.vue: vue-chartjs analytics (status doughnut + upload timeline bar chart)
  - App.vue: mobile hamburger menu with sidebar drawer and backdrop overlay
  - Responsive breakpoints added to all pages (860px, 640px, 540px)
  - New npm packages: pdfjs-dist, chart.js, vue-chartjs, marked
  - Version bumped to v1.5.0 everywhere (backend, frontend, README)
- **v1.5.1 Fixes & Enhancements:**
  - PdfViewer.vue: fixed pdfjs-dist v5 worker URL with Vite `?url` import pattern
  - ProfilePage.vue: `formatDateTime` shows "d. mmm yyyy ob HH:MM" for registration and last login
  - AdminPage.vue: dates updated to formatDateTime, enriched stats with 7 tiles + 3 charts (status doughnut, source bar, job doughnut)
  - ChatQA.vue: "Počisti" (clear chat) button with confirmation dialog, removes all Q&A for document
  - Backend: `DELETE /documents/{id}/answers` endpoint for bulk clearing Q&A history
  - Backend: `DELETE /documents/{id}/answers/{answerId}` endpoint for single answer deletion
  - Backend: admin/stats now returns storage_bytes, status_breakdown, source_breakdown, job_breakdown
  - Backend: CORS updated to include PATCH method (was missing, needed for admin role endpoint)
  - Backend: OpenAPI description updated to reflect full feature set (23 endpoints)
  - Backend: version bumped to v1.5.1
  - README updated to v1.5.1 with new endpoint table
  - Report updated with v1.5.0 + v1.5.1 feature descriptions, corrected endpoint count, technology table expanded
- **v1.5.2 Feature Bundle:**
  - Phase 42: UploadSection.vue rewritten for multi-file upload with per-file progress bars and batch upload
  - Phase 43: Document tags — Alembic migration 003, JSON tags column, PATCH endpoint, tag chips in DocumentCard, tag filter in DocumentsPage
  - Phase 44: AI summary prompts updated to request structured markdown, DocumentCard renders with marked.js + v-html
  - Phase 45: OnboardingWizard.vue component with 4-step wizard, localStorage persistence, enhanced empty state with step hints
  - ChatQA.vue: refactored inline multi-statement handler to method (prettier compatibility)
  - CI fixes: removed unused `case` import from admin.py, formatted all files with prettier
  - API endpoint count: 24 (added PATCH /documents/{id}/tags)
  - Backend: version bumped to v1.5.2
  - Frontend: version bumped to v1.5.2
  - README and report updated

### Immediate next steps

1. Capture the mandatory 16 screenshots for the Word report, plus 4 optional GUI screenshots (PDF viewer, chat Q&A, charts, mobile layout)
2. Render both Mermaid diagrams (`architecture.mmd`, `data-flow.mmd`) to PNG and insert them into the report
3. Unify the final written materials around the actual current numbers: 24 endpoints, 6 CI/CD jobs, 111 tests, 87% coverage, 70% CI threshold
4. Add one honest limitations subsection to the report: BackgroundTasks durability, missing frontend pagination, localStorage JWT trade-off, markdown sanitization follow-up
5. Rehearse a short defense flow on https://doc-ai-assist.com: login, upload, summarize, ask, download, admin, Swagger

## Proposed phases for v1.5.0 (GUI & Feature Overhaul)

The following phases target a significant upgrade of the user interface and frontend functionality. These are prioritized by impact on the professor demo experience and report quality.

### Phase 38 — In-App PDF Viewer (HIGH IMPACT) ✅ IMPLEMENTED
**Goal**: Embed a PDF viewer so users can read documents without downloading.
- Integrated `pdfjs-dist` (Mozilla PDF.js) as `PdfViewer.vue` component
- Shows PDF in a modal overlay when user clicks "Preberi" button on document card
- Supports page navigation, zoom in/out, keyboard shortcuts (Esc, arrows)
- Full mobile responsive (fills screen on small devices)
- **Status**: Completed in v1.5.0

### Phase 39 — Chat-Style Q&A Interface (HIGH IMPACT) ✅ IMPLEMENTED
**Goal**: Replace the flat Q&A cards with a modern chat-bubble interface per document.
- Created `ChatQA.vue` component with chat-bubble conversation thread
- User questions right-aligned (purple gradient), AI answers left-aligned with avatar
- Auto-scroll to latest message
- Typing indicator animation (bouncing dots) while AI processes
- Markdown rendering of AI responses via `marked` library
- Timestamps and source badges inline, delete button per answer
- **Status**: Completed in v1.5.0

### Phase 40 — Dashboard Analytics with Charts (MEDIUM IMPACT) ✅ IMPLEMENTED
**Goal**: Add visual charts to the Documents page.
- Integrated `chart.js` + `vue-chartjs` for doughnut and bar charts
- Document status distribution doughnut chart (ready/processing/pending/failed)
- Upload timeline bar chart (documents by month)
- Charts appear when user has 2+ documents
- Custom color scheme matching app theme
- **Status**: Completed in v1.5.0

### Phase 41 — Responsive Mobile Layout (MEDIUM IMPACT) ✅ IMPLEMENTED
**Goal**: Make the entire app work well on mobile and tablet screens.
- Hamburger menu button appears on mobile (< 860px)
- Sidebar opens as drawer overlay with backdrop dimming
- Stack stat cards and charts vertically on narrow screens
- Document cards wrap action buttons on mobile
- Landing page single-column on mobile, hidden nav links
- Admin page responsive table
- All breakpoints: 860px (tablet), 640px (mobile), 540px (small mobile)
- **Status**: Completed in v1.5.0

### Phase 42 — Multi-File Upload with Progress Bars (LOW-MEDIUM)
**Goal**: Allow users to upload multiple PDFs at once with visual progress tracking.
- Drag-and-drop multiple files
- Per-file progress bars during upload
- Queue visualization (uploading, waiting, done)
- Batch summary generation after multi-upload
- **Why**: Improves the practical usability of the upload feature.

### Phase 43 — Document Tags & Folders (LOW-MEDIUM)
**Goal**: Let users organize documents with tags and virtual folders.
- Backend: `tags` field on Document model (JSON array or separate table)
- Frontend: tag chips on document cards, filter by tag
- Create/rename/delete tags
- Optional: folder-like tree navigation in sidebar
- **Why**: Demonstrates a more realistic document management use case and adds visual richness.

### Phase 44 — Enhanced Summary Display with Markdown (LOW)
**Goal**: Render AI summaries as formatted markdown instead of plain text.
- Use `marked` or `markdown-it` to render summary_text
- Support bullet points, headers, bold/italic from AI output
- Prompt engineering: instruct AI to respond in structured markdown
- **Why**: Makes AI output look professional and structured.

### Phase 45 — Onboarding Wizard & Enhanced Empty States (LOW)
**Goal**: Guide new users through the app with a first-time onboarding flow.
- Step-by-step wizard: "Welcome → Upload your first document → Generate a summary → Ask a question"
- Better empty states with illustrations on all pages
- Tooltip hints on key elements
- **Why**: Polish that makes the app feel complete and user-friendly.

### Priority recommendation for v1.5.0

All four high/medium priority phases have been implemented:
1. ✅ **Phase 38 (PDF Viewer)** — PdfViewer.vue with pdfjs-dist
2. ✅ **Phase 39 (Chat Q&A)** — ChatQA.vue with marked, chat bubbles
3. ✅ **Phase 41 (Mobile layout)** — hamburger menu, responsive breakpoints
4. ✅ **Phase 40 (Charts)** — vue-chartjs doughnut + bar charts

New packages added: `pdfjs-dist`, `chart.js`, `vue-chartjs`, `marked`

Remaining v1.5.x phases (42–45) are optional stretch goals.

## Verification log

- Python 3 is available on the machine.
- Initial scaffold assumptions about local Node and Docker availability were later superseded by the user's verified shell output.
- Python-level scaffold can be validated now.
- Python source compilation succeeded after the first scaffold.
- Python source compilation succeeded after the persistence refactor.
- Python source compilation succeeded after the upload and storage integration step.
- Python source compilation succeeded after the summary integration step.
- Docker Compose configuration resolves successfully.
- The user validated that `node -v` and `npm -v` work in the target shell.
- The user validated that `docker ps` and `docker compose version` work in the target shell.
- The user validated that `docker compose build` completes successfully for backend and frontend images.
- End-to-end runtime verification with `docker compose up` is still pending in this agent session.

## Documentation rule

After every completed implementation phase:

1. update this master file
2. add or update the dedicated phase file
3. record what changed, what was tested, and what remains open

## Delta for current step

### Enhancement phases (post-initial implementation)

**Phase E1: Production fixes**
- Frontend Dockerfile converted to multi-stage build (dev → build → production with nginx)
- Backend Dockerfile updated with non-root user (appuser)
- Added .dockerignore files for frontend and backend
- Added startup validation rejecting default SECRET_KEY in production
- CORS tightened from wildcard to specific methods/headers
- docker-compose.yml and docker-compose.prod.yml updated with build targets

**Phase E2: Security improvements**
- Nginx default.conf rewritten with security headers (CSP, X-Frame-Options, etc.) and gzip
- TLS/HTTPS template created at infrastructure/nginx/ssl.conf
- slowapi rate limiting on auth (5/min) and AI endpoints (10/min)
- Input validation: question length 3–500 chars, password 8–128 chars

**Phase E3: Database migrations**
- Alembic initialized with initial migration for all 4 tables
- alembic.ini, env.py, and migration template created

**Phase E4: Frontend componentization**
- App.vue refactored from ~700 lines to ~160 lines
- Created AuthPanel.vue, UploadSection.vue, DocumentCard.vue components

**Phase E5: Backend improvements**
- Structured JSON logging with structlog
- Global exception handlers (422 validation, 500 no traces, 429 rate limit)
- Session management fix in processing_service.py
- Pagination on GET /documents with skip/limit/total

**Phase E6: Testing expansion**
- Added test_auth.py (8 tests) and test_documents.py (11 tests)
- Enhanced conftest.py with shared fixtures (mock_storage, mock_ai, auth_headers)
- Added pytest-cov for coverage reporting
- Total: 30 test cases across 4 files

**Phase E7: CI/CD improvements**
- Added ruff linting step to CI pipeline
- pytest-cov with --cov-fail-under=70 in CI
- Deploy script enhanced with Alembic migration and health check
- Created .env.production.example and pyproject.toml with ruff config

**Phase E8: Documentation and OpenAPI**
- All endpoints now have summary and description parameters
- README.md completely rewritten with architecture, security, testing sections
- API endpoint table added to README

**Phase E9: Report finalization**
- Security section expanded with rate limiting, headers, OWASP Top 10 mapping, JWT trade-off
- Cost table with real Hetzner CX33 pricing and PaaS comparison
- Implementation validation section updated with 30 test cases, CI pipeline details
- References expanded from 7 to 16 sources

**Phase E10: Final audit fixes**
- Fixed OPENAI_API_KEY default in .env and .env.example (was truthy placeholder, now empty for fallback mode)
- Added /redoc proxy location to both Nginx configs (default.conf and ssl.conf)
- Exposed backend port 8000 in dev docker-compose.yml; hidden via ports: [] in prod overlay
- Updated /api/v1/status features list to reflect all current capabilities
- Added summary/description to /health and /ready endpoints for OpenAPI completeness
- Fixed .gitignore to preserve .env.production.example
- Removed unused logging import from main.py

**Phase E12: Version 1.1.1 — Delete documents, OpenAI config fix, UX polish**
- Added DELETE /api/v1/documents/{id} endpoint with cascading removal of related Q&A records and processing jobs
- Added delete_object() to StorageService for MinIO file removal
- Added delete() to DocumentRepository and delete_for_document() to QuestionAnswerRepository and ProcessingJobRepository
- Added delete_document() to DocumentService orchestrating storage + DB cleanup
- Frontend: delete button on DocumentCard with inline confirmation overlay (backdrop-blur, cancel/confirm)
- Frontend: deleteDocument() API function, handleDelete() handler in App.vue
- Fixed OpenAI API key handling: added field_validator to convert empty string to None in Settings
- Added .env comments guiding users to set OPENAI_API_KEY for real AI summaries
- UX improvements: document card hover effects, creation date display, smooth TransitionGroup animations for document list add/remove, improved empty summary state with actionable hint
- formatBytes() now handles MB-sized files
- Version bumped to v1.1.1 in footer, README, and docs
- Complete frontend redesign: Inter font, CSS custom properties, card-based responsive layout
- App.vue: navbar with logo/version badge, hero section with gradient, footer with v1.1 branding
- AuthPanel.vue: pill-style tab navigation, modern form styling
- UploadSection.vue: drag-and-drop upload zone with file preview and cancel
- DocumentCard.vue: color-coded status badges, sectioned summary/Q&A display
- Nginx CSP relaxed for development (allows Google Fonts, WebSocket, inline scripts)
- WebSocket proxy added for Vite HMR (`/@vite/` and `/` locations)
- ssl.conf updated to match default.conf (WebSocket proxy, buffer tuning, gzip)
- PostgreSQL healthcheck added to docker-compose.yml (`pg_isready`, interval 5s, retries 5)
- Backend depends_on with `condition: service_healthy` for reliable startup order
- bcrypt pinned to 4.0.1 for passlib compatibility on Python 3.13
- Rate limiting disabled in test environment (`APP_ENV=test`)
- Test isolation improved: `drop_all` + `init_db` between test runs
- API URL changed from absolute `http://localhost:8000` to relative `/api/v1`
- Seed script fixed: sys.path.insert for module resolution, scripts/ added to Docker image
- All 30 tests passing, full E2E demo verified

**Phase E13: Version 1.1.2 — Comprehensive GUI overhaul**
- Overhauled `main.css` design tokens: gradient mesh background (layered radial-gradients on `<body>`), enhanced shadow scale (xs/sm/md/lg/glow), new CSS variables (`--border-subtle`, `--surface-raised`, `--primary-glow`, `--shadow-glow`, `--radius-xl`), `background-attachment: fixed`, `:focus-visible` outline
- App.vue: glassmorphism navbar (`backdrop-filter: blur(16px)`, semi-transparent `rgba`), gradient brand logo, brand subtitle, user avatar with initial letter, hero glow radial gradient, gradient text headline (`background-clip: text`), colored pill dots, technology tags row (Vue 3, FastAPI, PostgreSQL, Docker, Groq AI), dashboard header with stat cards (document count + summary count), improved empty-state illustration, right-aligned toasts with colored side bar + close button
- AuthPanel.vue: header with gradient icon wrap, SVG icons in tabs and form labels, gradient submit button with glow shadow, `<Transition>` form-switch animation, inputs with surface-alt background
- DocumentCard.vue: gradient icon wrap, status dots, separated action group, summary section with left-border accent, chat-bubble styled Q&A answers (question in surface, answer in primary-light), circular delete-confirm icon, answer enter transition
- UploadSection.vue: circular icon wrap, "Izberi datoteko" as gradient button, format hint text, file-icon gradient wrap, `<Transition>` upload-switch animation, inset shadow on drag-over
- Added Groq as primary AI provider (free tier, Llama 4 Scout) — provider chain: Groq → Gemini → OpenAI → fallback
- Version bumped to v1.1.2 in footer, README, and docs

**Phase E14: Version 1.2.0 — Admin, download, RAG-lite, Prometheus, expanded frontend**
- Backend: `GET /api/v1/admin/users` and `GET /api/v1/admin/stats` with admin role middleware
- Backend: `GET /api/v1/documents/{id}/download` with StreamingResponse and ownership check
- Backend: RAG-lite BM25 chunking in `summary_service.py` — text split into overlapping 800-word chunks, ranked by BM25 (k1=1.5, b=0.75), top 5 chunks sent to AI for Q&A
- Backend: Prometheus metrics via `prometheus-fastapi-instrumentator` at `/metrics`
- Backend: `/api/v1/status` features list updated to reflect all capabilities
- Frontend: search bar filtering documents by filename
- Frontend: sort dropdown (date, name, size, status)
- Frontend: user profile card (email, role, registration date)
- Frontend: admin dashboard panel with system stats and user list (visible to admin role)
- Frontend: download button on DocumentCard
- Frontend: version bumped to v1.2.0
- CI/CD: added Docker image build step in GitHub Actions
- CI/CD: fixed duplicate `run:` bug in ci.yml
- Infrastructure: `/metrics` proxy location in Nginx default.conf
- Testing: 9 new tests (admin stats/users with admin role, 403 for regular users, 401 unauthorized, download happy/404/cross-user, metrics endpoint)
- Total test suite: 39 tests across 5 files, all passing

### Previous deltas added phase 05 documentation
- added JWT-based auth with persistent SQLAlchemy-backed users
- added phase 07 documentation for data and storage baseline
- introduced document metadata model to support the next upload phase
- added phase 08 documentation for MinIO storage integration and upload endpoints
- implemented authenticated upload and per-user document listing endpoints
- added phase 09 documentation for AI-backed summary generation with local fallback
- implemented document summarize endpoint on top of stored PDFs
- added phase 10 documentation for document Q&A
- implemented document ask endpoint with persisted question-answer records
- added phase 11 documentation for frontend auth and dashboard flows
- implemented Vue flow for login, registration, upload, listing, and summary actions
- added phase 12 documentation for async summary and question jobs with polling
- added phase 14 documentation for hardened VPS deployment
- implemented async summary and question job creation with polling-visible results
- switched frontend summary action to async job polling flow
- switched frontend question action to async job polling flow
- refined document processing states with summary-processing, question-processing, summary-failed, and question-failed values
- added phase 13 documentation for OpenAPI examples and demo seed path
- added phase 16 documentation for observability baseline
- added schema-level OpenAPI examples, readiness endpoint, request logging, and demo seed script
- added phase 15 documentation for CI workflow
- added phase 17 documentation for backend flow testing
- added automated tests for upload, summarize, and ask endpoints with mocked storage and AI layers
- added runtime validation note for this machine
- added professor demo checklist
- added production rollout checklist
- added academic report outline
- added phase 18 documentation for costs and organizational fit
- aligned runtime notes with user-validated Docker and Node availability

**Phase E15: Version 1.2.1 — Massive GUI overhaul with sidebar layout and admin role management**
- Frontend: complete redesign from single-page scrolling to sidebar-based navigation
- Frontend: dark sidebar (#1a1d23) with collapsible toggle, page-based navigation (Dokumenti, Naloži, Profil, Admin)
- Frontend: user avatar and role badge in sidebar bottom, active page highlighting, document count badge
- Frontend: dedicated pages — documents with search/sort toolbar, upload, user profile card, admin dashboard
- Frontend: admin user table with data-table styling, role pills, promote/demote buttons
- Frontend: landing page for unauthenticated users with hero gradient text, feature dots, tech chips, AuthPanel
- Frontend: topbar with page title/subtitle and mini stats (document count, summary count)
- Frontend: toast notifications with colored accent bar, smooth transitions
- Frontend: responsive breakpoints at 860px and 540px for mobile support
- Backend: `PATCH /api/v1/admin/users/{user_id}/role` endpoint for admin role management
- Backend: `SetRoleRequest` Pydantic model with role validation, self-change protection
- Frontend API: `setUserRole(token, userId, role)` function in api.js
- main.css: removed `background-image: var(--bg-mesh)` from body (handled by landing page now)
- Version bumped to v1.2.1 in App.vue footer, sidebar brand, landing nav
- README updated: version title, API endpoint table (added download, admin, metrics, PATCH role)
- 39 tests still passing, all containers healthy

**Phase E16: Version 1.2.2 — Lint fixes, PDF extraction hardening, specs update**
- Fixed all 15 ruff lint errors (import sorting I001, missing newlines W292, unused import F401)
- Improved PDF text extraction: layout mode fallback when standard extraction yields <50 chars
- Proper HTTP 422 error for scanned/image-based PDFs instead of saving error message as summary
- Updated VPS specs from CX22 to CX33 (4 vCPU, 8 GB RAM, €5.49/month) across all docs
- Updated domain cost to €7.99/year (Namecheap) across all docs
- Version bumped to v1.2.2 in backend (FastAPI), frontend (package.json, App.vue), README

**Phase E17: Version 1.2.3 — Auto-formatters, CI format checks**
- Fixed persistent CI I001 errors by adding `[tool.ruff.lint.isort]` with `known-first-party = ["app"]` to pyproject.toml
- Added `[tool.ruff.format]` section (double quotes, space indent) and ran `ruff format` on all 36 Python files
- Added prettier (v3.5) as frontend devDependency with `.prettierrc` config (single quotes, no semicolons, trailing commas)
- Ran prettier on all Vue/JS/CSS frontend files
- CI backend-lint job now runs `ruff format --check` after `ruff check`
- CI frontend job now runs `prettier --check` before `npm run build`
- Deduplicated `ruff==0.11.13` line in requirements.txt
- Updated all stale docs: phase-15 (4 jobs, format checks), runtime-validation (39 tests, 4 jobs, formatters), architecture-and-dataflows (CI line), README (CI section, test count)
- Version bumped to v1.2.3 in backend (FastAPI), frontend (package.json, App.vue), README

**Phase E18: Version 1.2.4 — Comprehensive test coverage & CI improvements**
- Expanded test suite from 39 to **111 tests** across **9 files** with **87% measured backend coverage**
- Added `test_summary_service.py` (32 tests): chunking, BM25 ranking, AI provider dispatch with mocked httpx
- Added `test_delete_and_admin.py` (11 tests): document deletion, admin role management
- Added `test_storage_and_pdf.py` (16 tests): S3 storage operations, PDF text extraction
- Added `test_security.py` (9 tests): password hashing, JWT token creation/validation
- Fixed ruff I001 import sorting errors in new test files
- CI pipeline split from 4 to **6 jobs**: backend-lint, backend-test, frontend-lint, frontend-build, docker, deploy
- Added `FORCE_JAVASCRIPT_ACTIONS_TO_NODE24=true` for Node.js 24 compatibility
- Pinned `ubuntu-24.04` runner for reproducibility, switched to `npm ci` for deterministic installs
- Raised CI coverage threshold from 50% to 70%
- Fixed stale v1.2.1 version in App.vue landing footer
- Version bumped to v1.2.4 in frontend (package.json, App.vue), README

**Phase E19: Version 1.3.0 — Vue Router, CD, Grafana, backup encryption**

Changes:
- Vue Router 4 installed, 5 lazy-loaded routes: `/`, `/documents`, `/upload`, `/profile`, `/admin`
- Monolithic App.vue (1900 lines) split into shell + 5 page components + composable store
- Created `composables/useStore.js` with all shared reactive state and actions (module-level singletons)
- Navigation guards: redirect unauthenticated to landing, redirect guests away from protected routes
- `<router-link>` replaces manual `currentPage` state toggling in sidebar
- Each page component is a separate Vite chunk (code splitting)
- Added deploy job to GitHub Actions CI: SSH to VPS via `appleboy/ssh-action` after successful docker job, main branch only
- Added Prometheus container (prom/prometheus:v3.4.1) scraping FastAPI `/metrics` every 15s
- Added Grafana container (grafana/grafana:11.6.0) with auto-provisioned datasource and FastAPI dashboard
- Grafana dashboard panels: request rate, p50/p95 latency, in-progress requests, 24h total, 5xx error rate, response size
- Backup script enhanced: GPG AES-256 symmetric encryption (opt-in via `BACKUP_PASSPHRASE`), 7-day rotation, verification step
- Docker Compose updated with `prometheus`, `grafana` services and volumes
- Production overlay updated with restart policies for monitoring services
- Version bumped to v1.3.0 in backend (main.py), frontend (package.json, App.vue, LandingPage.vue), README

**Phase E20: Version 1.3.1 — Llama 4 Scout, prod fixes, lint fixes**

Changes:
- Upgraded primary AI model from Llama 3.3 70B to Llama 4 Scout 17B-16E (MoE, 750 tok/s, multimodal)
- Fixed Prettier lint failures in 3 Vue page components (AdminPage, DocumentsPage, LandingPage)
- Fixed docker-compose.prod.yml: mounted ssl.conf for production nginx (was missing — port 443 had no HTTPS config)
- Fixed docker-compose.prod.yml: removed duplicate port 80 mapping from prod overlay
- Updated .env.production.example and .env.example with new Groq model and added missing GROQ/GEMINI env vars
- Added .bak/.bak2 patterns to .gitignore
- Updated all docs (master plan, report, README) to reference Llama 4 Scout instead of Llama 3.3 70B
- Version bumped to v1.3.1 in backend (main.py), frontend (package.json, App.vue, LandingPage.vue), README

## Supporting operational documents

- `docs/professor-demo-checklist.md`
- `docs/production-rollout-checklist.md`
- `docs/runtime-validation.md`
- `docs/phase-18-costs-and-fit.md`
- `docs/architecture-and-dataflows.md`
- `report/00-report-outline.md`
- `report/01-report-draft.md`

## Diagram artifacts

- `docs/diagrams/architecture.mmd`
- `docs/diagrams/data-flow.mmd`

---

## Ocena projekta glede na zahteve naloge (MOŽNOST 3)

### Minimalne tehnične zahteve — stanje

| Zahteva | Status | Komentar |
| --- | --- | --- |
| REST API | ✅ Izpolnjeno | 24 endpointov, FastAPI, popolna OpenAPI dokumentacija |
| Integracija z oblačno storitvijo | ✅ Izpolnjeno | PostgreSQL, MinIO (S3), Groq/Gemini/OpenAI AI API |
| Gostovanje v oblaku | ✅ Izpolnjeno | Docker Compose + prod overlay, Hetzner VPS deployment potrjen na doc-ai-assist.com |
| Osnovni CI/CD | ✅ Izpolnjeno | GitHub Actions: ruff lint, pytest-cov, frontend build, auto-deploy via SSH |
| Dokumentacija API (OpenAPI) | ✅ Izpolnjeno | /docs (Swagger) + /redoc z opisi vseh endpointov |

### Elementi za višjo oceno — stanje

| Element | Status | Komentar |
| --- | --- | --- |
| Kontejnerizacija (Docker) | ✅ | Multi-stage builds, non-root containers, Docker Compose dev+prod |
| Kubernetes ali managed platforma | ❌ Ni implementirano | Ni potrebno za pozitivno oceno, dobro za bonus |
| Avtentikacija (JWT, OAuth2, OIDC) | ✅ | JWT HS256 z bcrypt, rate limiting |
| Integracija AI API ali LLM | ✅ | Groq (Llama 4 Scout) → Gemini → OpenAI → fallback |
| Monitoring ali logging | ✅ | structlog JSON logging, /health, /ready, Prometheus /metrics, Grafana dashboard |
| Infrastructure as Code | ❌ Ni implementirano | Ni Terraform/Ansible; Docker Compose je edini IaC |

### Ocenjevalni kriteriji naloge

| Kriterij | Delež | Ocena | Komentar |
| --- | --- | --- | --- |
| Tehnična globina | 30% | 8/10 | Solidna arhitektura, RAG-lite BM25 chunking za Q&A, multi-provider AI z fallback, Prometheus metrics, admin API. |
| Arhitekturna zasnova | 20% | 9/10 | Odlično: čista slojevita arhitektura, Mermaid diagrami, ločeni sloji (API → Service → Repository), Docker Compose dev/prod |
| Integracija in varnost | 20% | 8/10 | MinIO, 3 AI ponudniki, JWT, OWASP A01-A07, rate limiting, security headers, admin role-based access. Manjka: refresh tokeni |
| Analiza stroškov | 10% | 9/10 | Realne cene Hetzner, 3 scenariji, primerjava VPS vs. PaaS |
| Dokumentacija | 10% | 9/10 | 18+ faz + akademski report + diagrami. Odlično pokrito |
| Inovativnost | 10% | 7/10 | BM25 RAG-lite za kontekstualna vprašanja, multi-provider fallback, admin dashboard, search/filter/sort |

### KRITIČNE POMANJKLJIVOSTI

1. ~~**VPS deployment ni dokazan**~~ ✅ REŠENO 2026-03-11 — Aplikacija teče na Hetzner CX33 VPS, Ubuntu 24.04, https://doc-ai-assist.com, TLS Let's Encrypt, vseh 5 containerjev healthy.

2. ~~**Frontend je pretanek**~~ ✅ REŠENO v v1.2.0 — Dodano iskanje, sortiranje, prenos PDF, admin dashboard, user profil. Sedaj 12+ akcij.

3. ~~**Admin vloga obstaja v bazi, ni pa implementirana**~~ ✅ REŠENO v v1.2.0 — Admin middleware, GET /admin/users, GET /admin/stats, PATCH /admin/users/{id}/role, frontend admin panel.

4. ~~**AI integracija je plitva**~~ ✅ REŠENO v v1.2.0 — BM25 RAG-lite chunking: tekst se razdeli na segmente, rangira po relevantnosti za vprašanje, AI dobi samo top 5 chunkov.

5. ~~**CI/CD je samo CI, ni CD**~~ ✅ REŠENO v v1.3.0 — Dodan deploy job v GitHub Actions: SSH na VPS po uspešnem CI, avtomatski deploy ob push na main.

6. ~~**Report nima posnetkov zaslona**~~ ✅ ZAKLJUČENO — Report in outline posodobljena z vsemi screenshot placeholderji (16 posnetkov). Student mora zajeti posnetke in jih vstaviti v Word dokument.

### KAJ JE DOBRO (in zakaj naloga vseeno izpolnjuje zahteve)

Naloga zahteva demonstracijo razumevanja **celotnega tehnološkega konteksta** — arhitekture, integracije, varnosti, stroškov, realnega deployment-a. Studentov projekt to POKRIVA:

- Čista slojevita arhitektura (Vue → Nginx → FastAPI → PostgreSQL/MinIO/AI)
- Realna integracija 4 zunanjih storitev (PostgreSQL, MinIO, AI API-ji, Nginx)
- Varnostni model z JWT, rate limiting, ownership, security headers, OWASP
- Docker Compose za dev in prod z multi-stage builds
- CI pipeline z linting, testing, coverage
- Popolna dokumentacija z 18 fazami
- Dejanski tekoči sistem na produkcijskem VPS z javnim URL, TLS in CI/CD potjo

Student pravilno ugotavlja: AI del sam po sebi ni inovativen. Ampak **bistvo naloge ni AI inovacija** — bistvo je **integracija spletnih storitev v koherentno arhitekturo**.

---

## Predlagane nadaljnje faze (Phase 19+)

Spodnje faze so razvrščene po PRIORITETI — od najnujnejšega do nice-to-have.

### Phase 19: VPS deployment in dokazi ★★★ ✅ ZAKLJUČENO 2026-03-11

**Izvedeno:**
1. Deploy na Hetzner CX33 VPS (Ubuntu 24.04, 4 vCPU, 8 GB RAM, 80 GB disk)
2. Konfiguracija .env z produkcijskimi vrednostmi
3. Izvedba `deploy.sh` + alembic migrate — uspeh po 2 poskusih
4. Aktivacija TLS z Let's Encrypt za doc-ai-assist.com (velja do 2026-06-09)
5. Domena kupljena na Namecheap, A record nastavljen na 178.104.25.28
6. Vseh 5 containerjev healthy na produkciji
7. https://doc-ai-assist.com dostopen z HSTS, varnostnimi glavami

### Phase 20: Razširitev frontenda ★★ POMEMBNO

**Zakaj:** Trenutno ima GUI samo 5 akcij. Za "integrirano spletno storitev" je premalo.

Dodati:
1. **Download PDF** — gumb za prenos originalnega dokumenta (backend endpoint + frontend gumb)
2. **Iskanje/filter dokumentov** — iskalno polje po imenu datoteke
3. **Sortiranje** — po datumu, velikosti, statusu
4. **User profil stran** — prikaz email-a, števila dokumentov, datum registracije
5. **Responsive navigacija** — hamburger menu za mobile

### Phase 21: Admin funkcionalnost ★★ POMEMBNO

**Zakaj:** Admin vloga obstaja v bazi ampak ni implementirana. To je mrtva koda.

Dodati:
1. Admin middleware/decorator ki preverja `role == "admin"`
2. `GET /api/v1/admin/users` — seznam vseh uporabnikov
3. `GET /api/v1/admin/stats` — skupno število dokumentov, uporabnikov, povzetkov, Q&A
4. Frontend: admin dashboard stran z osnovnimi statistikami in seznamom uporabnikov
5. Admin ne sme brisati tujih dokumentov, ampak vidi statistike

### Phase 22: Izboljšana AI integracija (RAG-lite) ★★ POMEMBNO za inovativnost

**Zakaj:** Trenutna integracija je samo relay. Z RAG-lite pristopom postane sistem pametnejši od ChatGPT za specifične dokumente.

Dodati:
1. **Chunking** — razdelitev PDF teksta na segmente (po 500-1000 znakov)
2. **Relevance scoring** — BM25 ali TF-IDF prek chunkov za vprašanje
3. **Contextual Q&A** — AI dobi samo relevantne chunke, ne celotnega dokumenta
4. To NI polni RAG z vektorsko bazo, ampak je dovolj za demonstracijo pametnejšega iskanja
5. Prednost: boljši odgovori, manjša poraba tokenov, lažje pojasniti v reportu

### Phase 23: Prenos dokumentov (Download) ★ KORISTNO

**Zakaj:** Uporabnik lahko naloži dokument, ampak ga ne more prenesti nazaj. To je osnovna funkcionalnost.

Dodati:
1. `GET /api/v1/documents/{id}/download` — streaming response z original PDF iz MinIO
2. Frontend gumb "Prenesi" na DocumentCard
3. Ownership preverba (samo lastnik sme prenesti)

### Phase 24: Prometheus metrics endpoint ★ KORISTNO za višjo oceno

**Zakaj:** Trenutno ima samo structlog logging. Metrics endpoint pokaže razumevanje observability koncepta.

Dodati:
1. `/metrics` endpoint z osnovnimi metrikami (request count, duration, error rate)
2. Uporaba `prometheus-fastapi-instrumentator` Pythonove knjižnice
3. Opcijsko: docker-compose service za Prometheus + Grafana dashboard
4. Posnetki zaslona v report

### Phase 25: Zdravje CI/CD pipeline-a ★ KORISTNO

**Zakaj:** CI je samo CI, manjka CD del.

Koraki:
1. Popravi dupliciran `run:` v ci.yml (✅ že popravljeno)
2. Dodaj step za Docker image build v CI (preveri da se slika zgradi)
3. Opcijsko: GitHub Actions deploy step ki SSH-ja na VPS in požene deploy.sh
4. Dodaj badge v README (CI status)

### Phase 26: Report finalizacija s posnetki ✅ ZAKLJUČENO

**Status:** Report in outline v celoti posodobljena. 16 screenshot placeholderjev vstavljen v report draft. Stroškovna analiza, tehnološka tabela, zaključek, reference — vse posodobljeno na dejansko stanje (Groq, BM25, 111 testov, VPS €5.49, doc-ai-assist.com). Student mora zajeti posnetke in jih vstaviti v Word dokument.

Posnetki za 01-report-draft.md in Word dokument:
1. Posnetek 1: Arhitekturni diagram (Mermaid → PNG iz architecture.mmd)
2. Posnetek 2: Podatkovni tok diagram (Mermaid → PNG iz data-flow.mmd)
3. Posnetek 3: Landing page (https://doc-ai-assist.com) — hero, feature overview
4. Posnetek 4: Login / Registracija stran
5. Posnetek 5: Dashboard / Dokumenti — sidebar layout z dokumenti
6. Posnetek 6: Upload stran
7. Posnetek 7: AI summary — primer generiranega povzetka
8. Posnetek 8: Q&A — primer vprašanja in odgovora nad dokumentom
9. Posnetek 9: Admin panel — seznam uporabnikov, statistike, role management
10. Posnetek 10: User profil stran
11. Posnetek 11: Swagger UI (/docs) — lista endpointov
12. Posnetek 12: ReDoc (/redoc) — API dokumentacija
13. Posnetek 13: `curl -I https://doc-ai-assist.com` — varnostne glave + HSTS
14. Posnetek 14: `docker compose ps` na VPS — vseh 5 containerjev healthy
15. Posnetek 15: Terminal output `deploy.sh` — uspešen deployment
16. Posnetek 16: GitHub Actions CI — zelena pipeline

### Phase 27: Frontend UX izboljšave ✅ ZAKLJUČENO 2026-03-12

**Izvedeno:**
1. **Dark mode** — toggle v sidebaru, persistenca v localStorage, polne CSS spremenljivke za temno temo (html.dark)
2. **Stats dashboard kartice** — DocumentsPage prikazuje 4 statistične kartice (dokumenti, povzetki, vprašanja, % obdelanih)
3. **Kopiraj povzetek** — gumb "Kopiraj" na vsakem povzetku z clipboard API in vizualnim feedbackom
4. **Izboljšane AI animacije** — shimmer progress bar in pulse border med generiranjem povzetka ali odgovora
5. **questionsCount computed** — novo computed polje v store ki šteje vsa vprašanja čez vse dokumente

**Tehnični delta:**
- `frontend/src/assets/main.css` — dodan `html.dark` blok s polnim setom CSS custom properties
- `frontend/src/composables/useStore.js` — dodani `darkMode`, `toggleDarkMode()`, `questionsCount`
- `frontend/src/App.vue` — dark mode toggle gumb v sidebaru (ikona sonce/luna)
- `frontend/src/pages/DocumentsPage.vue` — 4 stat kartice nad toolbarom
- `frontend/src/components/DocumentCard.vue` — kopiraj gumb, `.is-processing` animacija



