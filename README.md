# AI Learning Lab
From Python Foundations to Intelligent Automation.

An AI-era software engineering learning platform: Python, Data, APIs, AI Models, AI Automation,
with a horizontal AI-Assisted Software Engineering track.

## Status
Phases 0 and 1 confirmed. Phase 2 (authentication) built. See docs/DEVELOPMENT_ROADMAP.md.

## Requirements
Python 3.11+, Node 20+, git. PostgreSQL is needed from Phase 2.

## Quick start
First time on a fresh clone:

    ./scripts/bootstrap.sh

Run both servers:

    ./scripts/dev.sh

- Frontend: http://localhost:5173
- API docs: http://127.0.0.1:8000/docs
- Health:   http://127.0.0.1:8000/api/v1/health

## Tests
    cd backend && .venv/bin/pytest
    cd frontend && npm test

## Layout
- backend/   FastAPI modular monolith (api, services, repositories, models, schemas, core, ai)
- frontend/  React + Vite + TypeScript + Tailwind
- curriculum/ lesson and exercise content as data (from Phase 3)
- docs/      architecture, design system, roadmap, development log, ADRs
- scripts/   bootstrap and dev scripts

## Docs
docs/PRODUCT_SPECIFICATION.md, SYSTEM_ARCHITECTURE.md, DATABASE_DESIGN.md, API_DOCUMENTATION.md,
DESIGN_SYSTEM.md, DEVELOPMENT_ROADMAP.md, DEVELOPMENT_LOG.md, ARCHITECTURE_DECISIONS.md

## Phase 2: database and first admin
    ./scripts/setup_db.sh          # tunes PostgreSQL for low RAM, creates role + databases, writes backend/.env
    cd backend && .venv/bin/alembic upgrade head
    cd backend && .venv/bin/python -m app.cli create-admin --email you@example.com --display-name "Your Name"
Backend tests need the ailab_test database that setup_db.sh creates.
