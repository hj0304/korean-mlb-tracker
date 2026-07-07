# 태극기 펄럭이며 (Korean MLB Tracker)

미국 메이저리그(MLB)·마이너리그(MiLB)에서 뛰는 한국인 선수들의 **매일 경기 결과**와 **시즌 누적 스탯**을 한곳에 모아 보여주는 웹 앱입니다.

> 서비스명은 **태극기 펄럭이며**, 레포/프로젝트 식별자는 `korean-mlb-tracker`를 유지합니다.

[![Backend CI](https://github.com/hj0304/korean-mlb-tracker/actions/workflows/backend-ci.yml/badge.svg)](https://github.com/hj0304/korean-mlb-tracker/actions/workflows/backend-ci.yml)
[![Frontend CI](https://github.com/hj0304/korean-mlb-tracker/actions/workflows/frontend-ci.yml/badge.svg)](https://github.com/hj0304/korean-mlb-tracker/actions/workflows/frontend-ci.yml)
[![Deployed on Vercel](https://img.shields.io/badge/Vercel-deployed-black?logo=vercel)](https://korean-mlb-tracker-sabior-s-projects.vercel.app)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE)

## 라이브 데모

- **프론트엔드 (Vercel)**: https://korean-mlb-tracker-sabior-s-projects.vercel.app
- **백엔드 API (Northflank)**: https://p01--korean-mlb-tracker--2kktxxb6fz4b.code.run

## 스크린샷

<!-- TODO: 데스크탑 / 모바일 / 다크 모드 스크린샷 추가 (S3-02) -->

## 기술 스택

| 레이어 | 선택 |
|---|---|
| 백엔드 | Python 3.12, FastAPI, SQLAlchemy 2.0 (async), Alembic, Pydantic v2 |
| 프론트엔드 | Next.js 16 (App Router), TypeScript, Tailwind CSS v4, shadcn/ui, TanStack Query v5 |
| DB | PostgreSQL (Supabase) |
| ETL | GitHub Actions cron → MLB Stats API |
| 배포 | Vercel (프론트), Northflank (백), Supabase (DB) |
| 관측성 | Sentry, structlog |

## 로컬에서 실행하기

### 백엔드

```bash
cd backend
uv sync
cp .env.example .env
alembic upgrade head
uv run uvicorn app.main:app --reload
```

### 프론트엔드

```bash
cd frontend
npm install
cp .env.example .env.local
npm run gen:types
npm run dev
```

### ETL 잡

```bash
cd backend
uv run python -m app.jobs.run --job=roster_sync
uv run python -m app.jobs.run --job=daily_games --date=2026-05-18
uv run python -m app.jobs.run --job=season_stats
```

## 문서

- [PRD](docs/PRD.md) — 무엇을 왜 만드는가
- [Tech Spec](docs/TECH_SPEC.md) — 아키텍처, 스키마, 결정 사항
- [Roadmap](docs/ROADMAP.md) — 스프린트 계획과 진행 상황

## 라이선스

[MIT](./LICENSE)
