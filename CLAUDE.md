# CLAUDE.md

Behavioral guidelines + project-specific context for Claude Code. Read this file first, every session.

---

## Part A — Behavioral Guidelines (universal)

> Adapted from community LLM coding best practices. These bias toward caution over speed. For trivial tasks, use judgment.

### 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them — don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

### 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Self-check: "Would a senior engineer call this overcomplicated?" If yes, simplify.

### 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it — don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that **your changes** made unused.
- Don't remove pre-existing dead code unless asked.

The test: every changed line should trace directly to the user's request.

### 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:

```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria → independent looping. Weak criteria ("make it work") → constant rework.

---

## Part B — Project Context (Korean MLB Tracker)

### Project Overview

**Korean MLB Tracker** is a portfolio web app that aggregates daily game results and season stats for Korean MLB/MiLB players in one place. Full-stack: Python/FastAPI backend, Next.js/TypeScript frontend, PostgreSQL on Supabase, scheduled ETL jobs hitting the unofficial MLB Stats API.

Primary documents:
- `docs/PRD.md` — what we are building and why
- `docs/TECH_SPEC.md` — how it is built (architecture, schema, decisions)
- `docs/ROADMAP.md` — sprint plan, current sprint, task list

**If a request conflicts with these documents, apply Part A §1: stop and ask before changing scope.**

### Tech Stack

| Layer | Choice |
|---|---|
| Backend | Python 3.12, FastAPI, SQLAlchemy 2.0 (async), Alembic, Pydantic v2 |
| External API | MLB Stats API (`statsapi.mlb.com`), via `MLB-StatsAPI` package or `httpx` |
| DB | PostgreSQL (Supabase) |
| ETL | GitHub Actions cron → `python -m app.jobs.run --job=<name>` |
| Frontend | Next.js 14 (App Router), TypeScript strict, Tailwind CSS, shadcn/ui, TanStack Query v5, Recharts |
| Deploy | Vercel (frontend), Northflank (backend), Supabase (db) |
| Observability | Sentry, Vercel Analytics, structlog |
| Tests | pytest (backend), Vitest (frontend) |

### Repository Layout

```
korean-mlb-tracker/
├── backend/        # FastAPI app + ETL jobs
├── frontend/       # Next.js app
├── docs/           # PRD, TECH_SPEC, ROADMAP, ADRs
└── .github/workflows/
```

Detailed tree: `docs/TECH_SPEC.md` §7.

### Conventions

#### Python (backend)
- Formatter/linter: **ruff** (`ruff check`, `ruff format`).
- Type checker: **mypy** strict (incremental).
- Imports: stdlib → third-party → first-party, blank lines between groups.
- Naming: `snake_case` for functions/vars, `PascalCase` for classes.
- Public functions in `services/` have docstrings.
- Async by default for I/O. `asyncio.TaskGroup` for parallel fetches.
- No raw SQL outside `db/`. Use SQLAlchemy.
- Pydantic models live in `schemas/`, NOT in `db/models.py`.

#### TypeScript (frontend)
- Strict mode. **`any` is forbidden**; prefer `unknown` + narrowing.
- Function components only.
- Files: `PascalCase.tsx` for components, `camelCase.ts` for utilities.
- Server Components by default; `"use client"` only when state/effects/browser APIs required.
- Data fetching: TanStack Query hooks in `lib/queries.ts`. Not scattered in components.
- API client: single `lib/api.ts`. Types auto-generated from backend OpenAPI via `npm run gen:types`.
- Styling: Tailwind. For conditional styles, use `cn()` (clsx + tailwind-merge).

#### Git
- Branch: `s<sprint>-<ticket>-<slug>` (e.g. `s1-04-stats-transformer`).
- Conventional Commits: `feat:`, `fix:`, `refactor:`, `test:`, `docs:`, `chore:`.
- PR title = commit title. PR body links the ROADMAP ticket.

#### Tests
- New service functions need at least one unit test.
- `services/stats_transformer.py` is the most critical — every transformation has a snapshot test using fixtures in `tests/fixtures/mlb_responses/`.
- Integration tests use real Postgres via `testcontainers-postgres`.
- Frontend: test what you'd test manually. Don't chase coverage numbers.

### Run Locally

```bash
# backend
cd backend
uv sync
cp .env.example .env
alembic upgrade head
uv run uvicorn app.main:app --reload

# frontend
cd frontend
npm install
cp .env.example .env.local
npm run gen:types
npm run dev

# ETL jobs
cd backend
uv run python -m app.jobs.run --job=roster_sync
uv run python -m app.jobs.run --job=daily_games --date=2026-05-18
uv run python -m app.jobs.run --job=season_stats
```

### External API Notes

- MLB Stats API is **unofficial**: no key, no SLA, undocumented but stable.
- Base: `https://statsapi.mlb.com/api/v1`
- `sportId`: 1 = MLB, 11 = AAA, 12 = AA, 13 = High-A, 14 = Low-A.
- Korean player IDs seeded in `app/core/config.py` (`KOREAN_PLAYER_IDS`).
- **Never call this API from the user-request path.** Always hit our DB. ETL keeps DB fresh.
- New endpoint/field → save raw JSON to `tests/fixtures/mlb_responses/` + add snapshot test.

### Current Sprint

See `docs/ROADMAP.md`. Currently: **Sprint 0**. First ticket: **S0-01**.

When I say "start the next ticket", pick the lowest-numbered unchecked one in the current sprint.

### Useful Commands

```bash
# backend
uv run ruff check . && uv run ruff format .
uv run mypy app
uv run pytest -q
uv run alembic revision --autogenerate -m "msg"
uv run alembic upgrade head

# frontend
npm run lint
npm run typecheck
npm run test
npm run build
npm run gen:types
```

### Things NOT To Do

- Don't add live game polling. Completed-game data only.
- Don't add auth, comments, or social features (PRD §3 Non-goals).
- Don't normalize the `stats` JSONB into wide columns until a real query pattern demands it.
- Don't call `statsapi.mlb.com` from anywhere other than `services/mlb_client.py`.
- Don't use `any` in TypeScript.
- Don't push directly to `main`. PRs only.

---

## Part C — Working Together

These are the working agreements between me (the developer) and you (Claude Code):

1. **Apply Part A always.** Before any non-trivial change, restate what you're about to do and confirm.
2. **One ticket = one PR.** If a request feels like 2+ tickets, say so and propose splitting (Part A §3).
3. **Read before writing.** Look at existing patterns in the file you're touching and its siblings. Match conventions.
4. **No silent dependency additions.** New package = one-line justification in PR description.
5. **Update docs when shape changes.** Schema change → migration + `TECH_SPEC.md` update. New decision → entry in `docs/adr/`.
6. **When I say "start"**, you re-read this file + the relevant ROADMAP ticket, then propose a plan before coding.
