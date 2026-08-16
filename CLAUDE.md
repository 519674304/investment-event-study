# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project is

A local, single-user web tool for investment event research ("证券事件 K 线研究工具"). A researcher queries K-line data for A-share stocks, industry indices, and concept indices, then marks manually-confirmed external information onto the chart by date to see the timing relationship between news and price.

Phase 1 is deliberately narrow: data organization + visualization only. The program does **not** judge lead/lag or do fundamental analysis; company systematic analysis is Phase 2 (a separate project).

`docs/` is the authoritative source of truth — requirements, domain design, responsibilities, architecture, and implementation plans — all written in Chinese. Every design doc has a stable Document ID (e.g. `ARCH-TECHNICAL`, `RESP-MAP`, `RESP-PROJECTION`). Start from `docs/00-index.md` and consult the relevant docs before implementing; the workflow is doc-first (design is approved in `docs/` before code).

## Layout

- `backend/` — Python (≥3.11) FastAPI + SQLAlchemy 2.0 + SQLite. Package `event_study` under `src/`.
- `frontend/` — React + TypeScript + Vite. Package manager is **pnpm** (use `pnpm`, not npm/yarn).
- `docs/` — requirements / domain / responsibilities / architecture / plans, plus a research-methodology skill under `docs/skills/`.

## Commands

### Backend (from `backend/`)
```bash
pip install -e ".[dev]"        # installs package (editable) + pytest/httpx
pytest                         # run all tests (config is in pyproject.toml)
pytest tests/test_health.py    # single test file
pytest -k <name>               # filter by test name
uvicorn event_study.api.app:create_app --factory   # run the API server
```
`pyproject.toml` sets `pythonpath=["src"]` and `testpaths=["tests"]`, so run pytest from `backend/`. `create_app` is a factory, hence `--factory`. With no `database_url` it uses SQLite at `%LOCALAPPDATA%\InvestmentEventStudy\event-study.db`; tests pass a `database_url` pointing at a `tmp_path` file for isolation.

### Frontend (from `frontend/`)
```bash
pnpm install
pnpm dev                       # Vite dev server
pnpm build                     # tsc -b && vite build
pnpm test                      # vitest run (jsdom; setup in src/test/setup.ts)
pnpm test src/App.test.tsx     # single test file
```

## Architecture

Single backend process serves both the API and the built frontend (no CORS, no separate server). Layering is lightweight DDD (see `docs/architecture/02-technical-architecture.md`):

```
UI (React) -> API DTO -> Application use cases -> Domain models/ports
                                                  ^
                                                  |
                             Infrastructure adapters (SQLite, external HTTP)
```

Hard rules future changes must respect:
- The **domain layer must not import FastAPI, SQLAlchemy, ECharts, or any data-source SDK.**
- UI only consumes API DTOs, never reads the DB schema.
- External adapters return source models; they never write the repository directly.
- No `utils` module as a dumping ground for mixed business rules.
- Planned backend modules are `catalog`, `market`, `discovery`, `events`, `shared`, `api` (see the module-boundary table in ARCH-TECHNICAL). Only `api` and `infrastructure` exist today; the SQLAlchemy records still live in `infrastructure/database.py`, so domain extraction has not happened yet.
- No Redis / queues / containers — single process + SQLite is a deliberate decision (ADR-008).

## Current implementation state (read before assuming features exist)

The roadmap (`docs/plans/00-roadmap.md`) is milestones M0→M6. Only M0/M1 are built:
- ✅ Research objects + events CRUD, many-to-many linking, SQLite persistence — all routes in `backend/src/event_study/api/app.py`.
- ✅ Frontend shell: object catalog sidebar + event list under a placeholder chart (`frontend/src/App.tsx`).
- ❌ Market data (M2), K-line chart + event projection (M3), information search (M4), and Windows packaging (M5) are **not** implemented. The chart is a hardcoded placeholder; there are no external data-source adapters yet.

Wiring gap to know about: the backend does not yet serve the built frontend (no `StaticFiles` mount in `app.py`), so the single-process serving model from ARCH-TECHNICAL is not wired up yet. `vite.config.ts` **does** proxy `/api` → `http://127.0.0.1:8000`, so in development run `uvicorn` (backend) and `pnpm dev` (frontend) together and the relative `/api/*` calls reach the API.

## Domain rules that are easy to get wrong

- **Research object identity** is `(market, code, type)`; re-POSTing an existing identity returns the existing object with HTTP 200 instead of creating a duplicate (201).
- **Events ↔ research objects is many-to-many**, and an event may be created **unlinked** (`linkedResearchObjectIds: []`). Deleting a research object only unlinks it — events are never cascade-deleted (deleting the last linked object leaves a valid "unlinked" event).
- **`publishedOn` is the real publication date and is always preserved.** The date an event lands on a K-line bar (`chartDate`) is computed by the projection at render time (non-trading days map to the previous bar) and is **never persisted** on the event entity.
- Event content + all its links must commit in a single transaction.
- Tags are currently stored as a newline-joined string (`tags_text`), not a normalized table (dedicated `tags`/`categories` tables are planned, not built).
- Unconfirmed search results are transient and must never be persisted — only user-confirmed input becomes an event.
- Structured problems use three severities: `TIP` (continue), `WARNING` (continue/degrade), `EXCEPTION` (abort, keep last valid state). The domain emits these; only the API boundary translates them to user-facing text.

## Testing notes

- Backend tests are integration-style: they build the app with `create_app(database_url=f"sqlite:///{tmp_path}/...")` and drive it through `fastapi.testclient.TestClient` (see `backend/tests/`). No DB-layer mocks.
- Frontend tests mock `globalThis.fetch` and assert on the rendered DOM (Testing Library + vitest + jsdom).
