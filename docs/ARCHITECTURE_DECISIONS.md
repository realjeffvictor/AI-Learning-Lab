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

ADR-020 Curriculum is stored as files (JSON plus Markdown) and loaded into PostgreSQL by an idempotent seed. Reason: content is reviewable in git and added without code changes. The seed never deletes; missing content is reported as an orphan.
ADR-021 Lesson availability is derived from the existence of the lesson Markdown file. Reason: the platform cannot show a lesson as available that has not been written.
ADR-022 Learning time is credited by the server, capped by elapsed wall-clock time since the previous heartbeat plus 5 seconds. Reason: client-reported time alone is trivially inflated.
ADR-023 Completing a lesson records concept exposure, not skill level. Reason: finishing a lesson is weak evidence of competence; levels will come from graded work.
ADR-024 Starting a lesson enrols the learner in its course. Reason: removes a pointless extra step; the explicit enroll button remains for adding a course without starting it.

ADR-025 Student code runs only in a Web Worker (plain script in public/, Pyodide from the jsDelivr CDN). The client enforces a timeout by terminating the worker; the next run starts a fresh one. Reason: untrusted code never touches the server or the main thread.
ADR-026 Network APIs are disabled inside the worker after Python loads. Reason: best-effort protection against accidents and casual abuse. It is not a security boundary; real isolation needs a cross-origin sandbox or a server-side execution service (future).
ADR-027 Code exercises are graded from test results reported by the browser; quizzes and puzzles are graded by the server. Reason: the server cannot run student code. Code scores are therefore self-reported, and certificates will rely on server-verifiable assessments and reviewed projects.
ADR-028 Exercises and curated resources are data files seeded into PostgreSQL. Recommendations only ever point at lessons and resources that exist in the database. Reason: no invented or dead links.
ADR-029 Mastery uses each exercise's latest attempt. Reason: retries should show current understanding, not accumulate.
ADR-030 The Pyodide version is read from the installed npm package, not hard-coded. Reason: no invented version numbers (ADR-009).

ADR-031 AIProvider is a small Protocol; OpenAI is called over plain httpx instead of the SDK. Reason: no SDK version drift, easy to test with httpx.MockTransport, easy to add other providers.
ADR-032 Assistance modes are prompt policy built on the server, and Independent mode refuses the call before any provider request. Reason: the browser cannot weaken or bypass a mode.
ADR-033 One orchestration service driven by assistant definitions instead of seven service classes. Reason: the assistants differ only in role prompts; separate classes would be duplicate code. Deviation from the Phase 0 plan.
ADR-034 Answer keys, test expectations and puzzle order are never placed in a prompt. Lesson text, exercise text and learner code are delimited and declared untrusted. Reason: prevents answer leakage and reduces prompt injection.
ADR-035 The study plan may cite only numbered database items, and any URL in the model output is stripped. Reason: no invented links (extends ADR-028).
ADR-036 Nothing is stored or counted when the provider call fails, and the database connection is released while waiting for the AI. Reason: failures are free for the learner, and slow provider calls cannot exhaust the small connection pool.
ADR-037 The API key is a SecretStr set through backend/.env by scripts/set_openai_key.sh. Reason: it never appears in logs, tracebacks, shell history or git.

ADR-038 Projects are data files (JSON plus a Markdown brief) seeded into PostgreSQL, with three kinds (build, architecture, code_review) that share one workspace and review flow. Reason: new projects need no code change, and architecture and code-review assessments reuse the same evaluation pipeline.
ADR-039 Project evaluation is human review against a four-criterion rubric (understanding, implementation, verification, ownership) mapped to the U, B, V, O principles. Approval needs 2+ on every criterion. Reviewers cannot review their own work and cannot see drafts. Reason: understanding and maintainability cannot be measured by auto-grading.
ADR-040 GitHub links are validated by format only and never fetched by the server. Reason: fetching user-supplied URLs invites server-side request forgery and rate-limit problems; the reviewer opens the link.
ADR-041 Achievements are defined in code and derived from evidence already in the database; earned_at is the evidence time. perfect-score counts only server-graded quizzes and puzzles. Reason: they cannot be faked by self-reported code scores, and no changes to earlier services were needed.
ADR-042 Review history is kept in project_reviews, and a submission is locked while awaiting review or approved. Reason: learners cannot change work under a reviewer, and feedback survives resubmission.

ADR-043 Content edited in the app is flagged managed_in_app, and the file-based seed skips flagged rows and reports them. Reason: files and the app are both editors of the same rows, and a silent overwrite would destroy work.
ADR-044 Exercise definitions edited in the app go through the same loader validators as the curriculum files. Reason: one definition of "valid", so the grader can always handle what the app stores.
ADR-045 Staff (instructor and admin) share content, student and analytics permissions. Only admins change roles or deactivate accounts. Reason: instructors teach; account security stays with admins. Per-instructor content ownership is deferred.
ADR-046 Published lessons cannot be emptied, and exercises with submissions cannot be deleted. Reason: learner progress and history must never dangle.
ADR-047 Notifications are rows polled by the client every 60 seconds. Reason: no websocket or queue infrastructure is justified yet; email and push can be added behind the same notification_service.create.
