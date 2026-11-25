# Architecture Decision Records

ADR-001 Modular monolith backend. Reason: one team, one deploy, simpler transactions; boundaries kept clean for later extraction.
ADR-002 Pyodide in a Web Worker for execution. Reason: no server-side untrusted code; timeout by terminate/respawn. Limits documented.
ADR-003 Access token in memory + refresh token in HttpOnly cookie. Reason: reduces XSS token theft vs localStorage; enables revocation.
ADR-004 Argon2id password hashing (argon2-cffi). Reason: current best practice; bcrypt acceptable fallback.
ADR-005 Curriculum as data (DB + content files), idempotent seeding. Reason: add content without code changes.
ADR-006 Concept taxonomy drives scoring, competency, and recommendations. Reason: enables the weakness-to-resources loop.
ADR-007 Curated resources table; AI recommends only existing entries. Reason: prevents hallucinated links.
ADR-008 AI provider abstraction; assistance mode enforced server-side. Reason: provider swap; learners cannot bypass Mode 1/2 from the client.
ADR-009 Package versions are resolved at install (latest stable) and then pinned in lockfiles/requirements. Reason: avoids invented versions.
ADR-010 Tailwind with CSS-variable design tokens. Reason: consistent theming (light/dark) and no per-page drift.

## Security architecture (summary)
Auth: Argon2id, short JWTs, rotating hashed refresh tokens, login throttling. AuthZ: role guard dependencies + ownership checks
in services, tested with an authorization matrix. Input: Pydantic validation, parameterized queries only. Secrets: env vars, never
committed, .env.example only. AI: server-side keys, per-user quotas, prompt-injection-aware context handling (student code and
documents treated as untrusted data), no destructive actions without explicit user approval. Browser execution: isolated
worker, timeout, no tokens or cookies reachable from worker. Transport: HTTPS, strict CORS allowlist, security headers.
Audit: audit_logs for auth events, role changes, content edits, admin actions.

## Risks and mitigations
1. Scope too large: strict phase gating; sample content only, labelled honestly.
2. Pyodide limits (packages, size, load time): lazy load, cache, clear errors, future execution service.
3. AI cost/abuse: quotas, model config, caching, Mode 1 blocks calls.
4. AI inaccuracy: curated resources, grounding in lesson context, VERIFY-style prompts, user-facing disclaimers.
5. Generic-looking UI: tokens and motifs fixed now; review each phase against DESIGN_SYSTEM.md.
6. Auth mistakes: mature libraries, tests per role and route.
7. Version drift: pin and commit lockfiles.
8. Free-plan hosting cold starts: documented; health checks.

ADR-011 Tailwind v4 CSS-first configuration (tokens in src/design/theme.css, no tailwind.config.js). Reason: tokens live in one CSS file shared by light and dark themes.
ADR-012 Python dependencies installed wheel-only (--only-binary=:all:) and frozen to requirements.lock. Reason: no source compiles on low-memory machines; reproducible installs.
ADR-013 Request ID middleware and a single error envelope from the first endpoint. Reason: every later endpoint inherits consistent errors and traceable logs.

ADR-014 Synchronous SQLAlchemy 2.0 with psycopg 3 and a small pool. Reason: simpler, lower memory; FastAPI runs sync routes in a threadpool.
ADR-015 Refresh-token rotation with family revocation on reuse and a 10 second grace window. Reason: detects stolen tokens while tolerating two tabs refreshing at once. Reuse is audited only when a revocation actually happened.
ADR-016 Access tokens carry no role; every request reads the user from the database. Reason: demotion and deactivation take effect immediately.
ADR-017 First admin is created by CLI, never by the API. Reason: no self-service path to admin.
ADR-018 Login throttling is in-process for now. Reason: adequate for a single worker; replaced by shared rate limiting in Phase 8.
ADR-019 CSRF defence for cookie endpoints is SameSite plus a required custom header, enforced with the CORS allowlist.
