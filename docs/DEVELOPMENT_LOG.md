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
