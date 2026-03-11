# Phase 11 - Frontend Flows

## Purpose

Turn the Vue frontend from a visual placeholder into a usable client for the already-implemented backend API.

## Implemented changes

- added API helper layer for authentication and document endpoints
- implemented registration and login forms
- added bearer-token session handling in browser storage
- added authenticated dashboard with current user panel
- added PDF upload form
- added document list rendering with per-document summarize action
- added inline loading, success, and error feedback for critical operations

## Component architecture

The frontend was refactored from a monolithic `App.vue` (~700 lines) into a component-based structure:

- `App.vue` (~160 lines) — slim orchestrator with state management and API calls
- `AuthPanel.vue` — login and registration forms with emit-based parent communication
- `UploadSection.vue` — PDF file upload with local state management
- `DocumentCard.vue` — document display, summary trigger, Q&A interface, delete with inline confirmation

Each component is under 200 lines and communicates via props and emits.

## Covered user flows

### Authentication

1. user opens the application
2. user registers or logs in
3. token is stored in local browser storage
4. frontend loads the current user and personal documents

### Upload

1. authenticated user selects a PDF file
2. frontend sends a multipart upload request
3. document list refreshes after success

### Summary

1. user clicks summarize on a document
2. frontend calls the summarize endpoint
3. updated summary is shown in the document card

## Design direction (v1.1)

The frontend was redesigned in v1.1 with a modern, card-based visual system:

- **Typography**: Inter font loaded from Google Fonts CDN (weights 400–700)
- **Color system**: CSS custom properties (`--primary: #6366f1`, `--accent: #10b981`, `--bg`, `--surface`, `--border`, etc.)
- **Layout**: Responsive card grid with `backdrop-filter` navbar, hero section with gradient background, and sticky footer
- **Components**: Pill-style tab navigation in AuthPanel, drag-and-drop upload zone in UploadSection, color-coded status badges in DocumentCard
- **Branding**: Navbar displays "AI Document Assistant" with SVG icon and "v1.1" badge; footer shows "© 2025/26 Projektna naloga — ALMA MATER EUROPAEA · Verzija 1.1"
- **Responsive**: Mobile-safe breakpoints at 520px and 768px
- **API communication**: All requests use relative path `/api/v1` through the Nginx reverse proxy (no hardcoded hostnames)

## v1.1.1 updates

- **Delete document**: DocumentCard now includes a delete button (trash icon) with inline confirmation overlay using backdrop-blur. Deleting removes the file from MinIO, related Q&A records, processing jobs, and the document row.
- **UX improvements**: Document cards have hover effects (subtle border highlight + shadow lift). Creation date displayed as a badge. Smooth TransitionGroup animations for document list add/remove. Improved empty summary state with actionable hint ("Klikni Povzetek za generiranje AI povzetka").
- **OpenAI config fix**: Settings validator converts empty `OPENAI_API_KEY` string to `None`, preventing ambiguity. Comments added to `.env` guiding the user.
- **Version**: Footer updated to v1.1.1.

## v1.1.2 updates — GUI overhaul

- **Design tokens**: Overhauled `main.css` with gradient mesh background (`radial-gradient` layers on `<body>`), enhanced shadow scale (xs/sm/md/lg/glow), new variables (`--border-subtle`, `--surface-raised`, `--primary-glow`, `--shadow-glow`, `--radius-xl`), and `background-attachment: fixed`.
- **Navbar**: Glassmorphism effect with `backdrop-filter: blur(16px)` and semi-transparent background.
- **Hero section**: Animated radial glow behind the hero, gradient text headline (`background-clip: text`), colored pill dots, technology tags row (Vue 3, FastAPI, PostgreSQL, Docker, Groq AI).
- **Dashboard**: Header bar with stat cards (document count, summary count), improved empty-state illustration.
- **AuthPanel**: Header with gradient icon, SVG icons in tabs and form labels, gradient submit button with glow shadow, `<Transition>` form-switch animation.
- **DocumentCard**: Gradient icon wrap, status dots, separated action group, summary section with left-border accent, chat-bubble styled Q&A (question in surface, answer in primary-light), circular delete-confirm icon.
- **UploadSection**: Circular icon wrap, "Izberi datoteko" rendered as gradient button, format hint text, file-icon gradient wrap, `<Transition>` upload-switch animation, inset shadow on drag-over.
- **Toasts**: Right-aligned with colored side bar and close button.
- **Version**: Footer updated to v1.1.2.

## Limitations in this phase

- no router was introduced because the current MVP fits a single authenticated workflow screen
- no state-management library is needed at this scale
- JWT stored in localStorage (documented security trade-off)

## Verification

- editor diagnostics reported no immediate file errors in the updated frontend files
- ~~actual browser runtime validation remains pending until Node tooling is installed~~ — resolved: Node.js confirmed available, frontend builds and runs successfully via Docker Compose

## Next step

Add document question-answer interactions and then wire the frontend to asynchronous processing states.

## Delta — v1.2.0 and v1.2.1

**v1.2.0:** Added search bar, sort dropdown (date/name/size/status), user profile card, admin dashboard panel with system stats and user list, download button on DocumentCard.

**v1.2.1:** Complete redesign from single-page scrolling layout to sidebar-based navigation:
- Dark sidebar (#1a1d23) with collapsible toggle, page-based navigation (Dokumenti, Naloži, Profil, Admin)
- User avatar and role badge in sidebar bottom, document count badge
- Dedicated pages: documents with search/sort toolbar, upload, user profile, admin dashboard
- Admin user table with role pills and promote/demote buttons (PATCH role endpoint)
- Landing page for unauthenticated users with hero gradient, feature dots, tech chips
- Topbar with page title/subtitle and mini stats
- Toast notifications with colored accent bars
- Responsive breakpoints at 860px and 540px
