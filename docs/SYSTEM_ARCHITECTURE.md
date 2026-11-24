# System Architecture

## Topology
Browser (React SPA, Vercel) → HTTPS/JSON → FastAPI modular monolith (Render) → PostgreSQL (managed).
FastAPI → AI provider (OpenAI) server-side only.
Python execution happens only in the browser (Pyodide in a Web Worker).

## Backend layers (dependencies point downward only)
- api/        FastAPI routers. Parse and validate input, call a service, return a schema. No business logic.
- services/   Business rules, transactions, authorization decisions, orchestration.
- repositories/ All SQLAlchemy queries. Parameterized only. No business rules.
- models/     SQLAlchemy ORM models.
- schemas/    Pydantic request/response models (separate from ORM models).
- core/       Settings (pydantic-settings), security (hashing, JWT), dependencies, logging, errors.
- ai/         AIProvider interface, OpenAI implementation, prompt policies per mode, assistant services, usage limiter.
- tests/      Unit (services), integration (API + test DB), authorization matrix tests.
Dependency injection via FastAPI Depends for sessions, current user, role guards, provider.

## Frontend architecture
- Feature-sliced: src/features/<feature>/{api,components,hooks,types}. Shared UI in src/components; tokens in src/design.
- Routing: React Router with route guards (UX only; the backend is the authority).
- Server state: TanStack Query. Local UI state: React state/context. No global store unless proven necessary.
- Typed API client in src/lib/api with one error-normalization point.
- Workspace: resizable split panels (lesson / editor / output / assistant), collapsing to tabs on small screens.
- Python runner: src/workers/pyodide.worker.ts. Protocol: run, result, stdout, stderr, timeout, terminate.
  Timeout kills and respawns the worker. Unsupported-package errors are surfaced clearly.
  Limitations documented: no OS access, limited packages, no threads/sockets, performance bounded, no cross-tab persistence.

## Curriculum as data
Courses, modules, lessons, exercises, puzzles and projects are rows plus content files (Markdown/JSON in curriculum/).
A seeding command imports them idempotently. Adding content requires no code change.
Exercise types: code (test-case based), quiz (MCQ/short), puzzle (ordering, bug-hunt, matching), project.
Every gradable item maps to concept_tags, enabling weakness analysis.

## Recommendation engine
On submission: score + per-concept results → service ranks weakest concepts → returns (a) platform lessons tagged with
those concepts, (b) curated resources from the resources table. The AI may explain and prioritize, but may only cite
items that exist in the database. It never invents links.

## Execution evolution path
Browser Pyodide now. Later: separate isolated execution service (containerized, no network, resource-limited) behind an
ExecutionBackend interface so the frontend contract does not change.

## Observability
Structured JSON logs with request IDs. audit_logs for sensitive actions. Error monitoring added in Phase 8.
