# Development Log

## Phase 0: Architecture and Design System
- Completed: blueprint documents drafted (this folder).
- Files created: README.md and all docs/*.md.
- Dependencies added: none.
- Tests: none (documentation only).
- Known limitations: none yet. Stack versions are decided at install time in Phase 1.
- Pending: user confirmation of the blueprint, including the five decisions in docs/ARCHITECTURE_DECISIONS.md.

## Phase 1: Project Foundation (2026-11-24)
- Phase 0 confirmed by the user; blueprint pushed to GitHub.
- Completed: FastAPI app factory, settings, JSON logging, request IDs, error envelope, CORS allowlist, /api/v1/health;
  React + Vite + TypeScript + Tailwind v4 app with design tokens, self-hosted fonts, typed API client, TanStack Query health check;
  dev and bootstrap scripts; .gitignore.
- Files: see git history (7 commits). Existing 0-byte placeholder files were replaced; frontend/tailwind.config.js removed (Tailwind v4 is CSS-first).
- Dependencies: backend in backend/requirements.lock (wheel-only install); frontend in frontend/package-lock.json.
- Tests: 10 backend (pytest), 4 frontend (vitest). Frontend component tests are planned for Phase 8.
- Known limitations: no database yet; health check is liveness only; no auth; Monaco, Lucide and charts not installed until needed.
- Pending: user confirmation that Phase 1 works end to end.

## Phase 2: Authentication and User Management (2026-11-24)
- Phase 1 confirmed by the user.
- Completed: PostgreSQL setup script (low-memory tuning); Alembic and migration 0001 (users, user_profiles, refresh_tokens, audit_logs);
  Argon2id hashing; JWT access tokens; rotating hashed refresh tokens with reuse detection; HttpOnly cookie plus CSRF header;
  login throttling; roles and backend authorization; profile and admin user APIs; audit log; admin bootstrap CLI;
  health check now reports database status; frontend login, register, dashboard, profile, admin users, protected routes.
- Bug found by tests and fixed: after a replay, the legitimate client's next refresh logged a second reuse alert.
  revoke_family now returns the number of tokens revoked and the audit row is written only when it is above zero.
- Files: see git history (commits are made manually by the user).
- Dependencies added: sqlalchemy, alembic, psycopg, argon2-cffi, pyjwt, email-validator (no new frontend packages).
- Tests: backend adds auth, security, users and database tests (run against the ailab_test database); frontend adds 3 session tests.
- Known limitations: login throttle is in-process and per worker (Phase 8); no email verification or password reset yet;
  behind a proxy the client IP needs forwarded-header handling at deployment; production cross-site cookies need
  COOKIE_SAMESITE=none with HTTPS (decided in Phase 8); no frontend component tests until Phase 8.
- Pending: user confirmation that Phase 2 works end to end.

## Phase 3: Curriculum and Learning Engine (2026-11-25)
- Phase 2 status: 69 backend tests and 7 frontend tests pass; browser sign-in was still unconfirmed when Phase 3 was requested.
- Completed: migration 0002 (concepts, courses, modules, lessons, lesson_concepts, enrollments, lesson_progress, user_competencies);
  curriculum files (34 concepts, 5 stage courses plus the AI-assisted engineering track, every module from the spec);
  loader with validation and an idempotent seed command; courses, lessons, enrollment and progress APIs;
  server-verified learning time; concept exposure tracking; frontend curriculum, course, module, lesson, progress pages and a new dashboard.
- Content honesty: only 4 lessons are written (what is programming, your first Python program, variables and names, the five principles).
  All other lessons and modules are listed as Planned. Availability is derived from the existence of the lesson Markdown file.
- Dependencies added: react-markdown (frontend). No new Python packages.
- Known limitations: no instructor editing yet (Phase 7); lessons contain static code, runnable editors arrive in Phase 4;
  competency data is exposure only, not skill level; planned lessons cannot be started; completing a lesson cannot be undone.
- Pending: user confirmation that Phase 3 works end to end.

## Phase 4: Interactive Learning and Python Playground (2026-11-25)
- Phase 3 status: 108 backend and 14 frontend tests passed; browser sign-in was still unconfirmed when Phase 4 was requested.
- Completed: migration 0003 (exercises, exercise_concepts, submissions, submission_concept_results, resources);
  exercise and resource loader plus idempotent seed; server-side grading for quizzes and puzzles; code grading from browser-reported test results;
  per-concept results; rule-based recommendations (platform lessons plus curated resources); attempt history; mastery by concept (latest attempt per exercise);
  Monaco editor (CDN, lazy, plain-textarea fallback); Pyodide Web Worker with timeout, Stop, unsupported-package errors and best-effort network blocking;
  playground page; exercise UI (quiz, code, puzzle) inside lessons; mastery section on the Progress page.
- Content: 8 exercises across the 4 written lessons and 8 curated resources. No YouTube video links were added because they could not be verified.
- Dependencies added: @monaco-editor/react (frontend), pyodide (dev dependency, used only to pin the CDN version). No new Python packages.
- Known limitations: code exercise scores are self-reported (the server cannot run student code); network blocking in the worker is best-effort, not a security boundary;
  only the Python standard library runs in the browser; input() is unavailable; Monaco and Pyodide need internet on first load;
  no rate limiting on submissions yet (Phase 8); recommendations are rule-based until the AI tutor arrives in Phase 5; exercises cannot be edited in the UI until Phase 7.
- Pending: user confirmation that Phase 4 works end to end.

## Phase 5: AI Learning and Development Assistants (2026-11-26)
- Phase 4 status: user reported everything passed.
- Completed: migration 0004 (ai_conversations, ai_messages, ai_usage_counters); AIProvider abstraction with an OpenAI implementation over httpx;
  seven assistants (tutor, code, debug, architecture, testing, docs, review) and five assistance modes enforced server-side (independent refuses the call);
  lesson-, exercise- and mistake-aware context; prompt-injection delimiters; per-user daily request and token limits; conversation storage;
  AI study plan grounded in database lessons and curated resources with URL stripping; frontend assistant panel in lessons, an assistant page, and the study plan on the Progress page.
- Dependencies: httpx moved to runtime requirements. No new frontend packages.
- Known limitations: no content moderation; answers are not streamed; attached code is sent to the provider but not stored; URL stripping is best-effort;
  one orchestration service instead of seven classes; ai_assistance_sessions, ai_interactions, code_artifacts, code_reviews and architecture_decisions tables are deferred
  (mode is stored per message); usage limits are per user, not global; the default model name must be checked against the provider's current list.
- Pending: user confirmation that Phase 5 works end to end with a real API key.

## Phase 6: Projects and Practical Evaluation (2026-11-26)
- Phase 5 status: user reported everything passed, with the assistants working on a real key.
- Completed: migration 0005 (projects, project_concepts, project_submissions, project_reviews, user_achievements);
  project loader and idempotent seed; three authored projects (expense tracker, review AI-generated code, choose an architecture);
  project workspace with draft, checklist, GitHub link, documentation and reflection; server-side submit rules; locking while awaiting review;
  reviewer queue and rubric review (understanding, implementation, verification, ownership; scores 1 to 4; approval needs 2+); review history;
  reviewers cannot review their own work and cannot see drafts; seven achievements derived from evidence.
- Dependencies: none new.
- Known limitations: repository links are checked by format only (the server never fetches them); architecture and code-review projects are graded by people only;
  the review queue is minimal until the Phase 7 instructor dashboard; no notifications when a review arrives (Phase 7); no certificates yet;
  achievements are synced when a project is submitted or reviewed and when the achievements list is opened;
  perfect-score counts quizzes and puzzles only because code scores are self-reported; some lessons the expense tracker relies on are still Planned.
- Pending: user confirmation that Phase 6 works end to end, including a review made by a second account.

## Phase 7: Administration and the Multi-User Platform (2026-11-26)
- Phase 6 status: user reported everything passed, including the two-account review flow.
- Completed: migration 0006 (notifications; managed_in_app on lessons, exercises and projects); staff dashboard with analytics (users by role, active learners, pending reviews,
  enrollments, most-completed lessons, exercise pass rates, AI usage); student list with search and filter; student detail; enrollment add and remove with notification;
  in-app lesson create and edit, exercise create, edit and delete (definitions validated by the same loader rules as files), project title, summary and brief editing;
  audit entries for every content change; notifications (review outcome, enrollment) with a header unread count and a notifications page;
  seeds skip content edited in the app and report it.
- Known limitations: any instructor can edit any content (no ownership) and there is no version history; editing an exercise changes the meaning of earlier attempts;
  exercise definitions are edited as JSON (no visual builder); lessons cannot be deleted or unpublished (learner progress refers to them); project requirements are read-only in the app;
  app-created lessons are listed in the seed warnings on every run; notifications are polled every 60 seconds (no push); no email notifications;
  analytics are live queries without caching, which is fine at this scale.
- Pending: user confirmation that Phase 7 works end to end (both roles).
