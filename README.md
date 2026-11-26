# AI Learning Lab
From Python Foundations to Intelligent Automation.

An AI-era software engineering learning platform: Python, Data, APIs, AI Models, AI Automation,
with a horizontal AI-Assisted Software Engineering track.

## Status
Phases 0 and 1 confirmed. Phase 2 (authentication) tested. Phase 3 (curriculum engine) tested. Phase 4 (playground and exercises) tested. Phase 5 (AI assistants) tested. Phase 6 (projects and review) tested. Phase 7 (administration) built. See docs/DEVELOPMENT_ROADMAP.md.

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

## Phase 3: curriculum
Curriculum content lives in curriculum/ as JSON and Markdown. A lesson is published only if its .md file exists.

    cd backend && .venv/bin/alembic upgrade head
    cd backend && .venv/bin/python -m app.seed --check    # validate only
    cd backend && .venv/bin/python -m app.seed            # load into the database (safe to re-run)

Add a lesson: list it in the course's course.json, add concept slugs from concepts.json, put the text in
curriculum/courses/<course>/<module-slug>/<lesson-slug>.md, then run the seed command.

## Phase 4: exercises and the Python playground
Exercises live in curriculum/exercises/<course>/<module>/<lesson>.json and curated resources in curriculum/resources.json.
Run `cd backend && .venv/bin/python -m app.seed` after editing them (use --check to validate only).
Monaco and Pyodide load from the jsDelivr CDN on first use, so the first run needs internet and downloads about 10 MB.
The Pyodide version is pinned by the pyodide dev dependency and written to frontend/src/features/python/pyodideVersion.ts.

## Phase 5: AI assistants
The assistants need an OpenAI API key (API billing is separate from a ChatGPT subscription).

    ./scripts/set_openai_key.sh      # stores the key in backend/.env without echoing it
    ./scripts/dev.sh                 # restart so the API picks it up

Without a key the app works normally and the assistant pages say the AI is switched off.
Limits per user per day default to 40 requests and 100,000 tokens (AI_DAILY_REQUEST_LIMIT, AI_DAILY_TOKEN_LIMIT in backend/.env).
Check the current model names at https://platform.openai.com/docs/models and set OPENAI_MODEL if the default is not available to you.

## Phase 6: projects and review
Projects live in curriculum/projects/<course-slug>/<project-slug>.json plus a matching .md brief.
Run `cd backend && .venv/bin/python -m app.seed` after editing them (use --check to validate only).
Instructors and admins review submitted work at /reviews. Nobody can review their own submission,
so test the flow with two accounts: a learner who submits and an admin or instructor who reviews.

## Phase 7: administration
Instructors and admins get a Manage area at /manage: dashboard, students, enrollment management, and editing of lessons, exercises and project briefs.
Content edited in the app is flagged and the seed command will not overwrite it (it prints a warning instead).
Only admins can change roles or deactivate accounts (/admin/users). Learners get notifications for reviews and enrollments.
