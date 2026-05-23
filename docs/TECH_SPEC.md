# Tech Spec — Korean MLB Tracker

> **상태**: Draft v1.0 · **작성일**: 2026-05-19 · **관련 문서**: PRD.md, ROADMAP.md

## 1. 시스템 컨텍스트

```
┌────────────────────────────────────────────────────────────┐
│                     사용자 (브라우저)                          │
└────────────────────────┬───────────────────────────────────┘
                         │ HTTPS
                         ▼
        ┌────────────────────────────────┐
        │    Next.js (Vercel)             │  ← 정적 페이지 + SSR + BFF
        │  - App Router                   │
        │  - TanStack Query (캐싱)         │
        └────────────────┬────────────────┘
                         │ REST (JSON)
                         ▼
        ┌────────────────────────────────┐
        │    FastAPI (Northflank)         │  ← API + 비즈니스 로직
        │  - /api/v1/players              │
        │  - /api/v1/players/:id/games    │
        └────────┬─────────────────┬──────┘
                 │                 │
                 ▼                 ▼
        ┌──────────────────┐  ┌────────────────────┐
        │ PostgreSQL       │  │ ETL Worker          │
        │ (Supabase)       │◀─│ (APScheduler        │
        │                  │  │  in FastAPI proc 또는│
        │                  │  │  GitHub Actions cron)│
        └──────────────────┘  └─────────┬──────────┘
                                        │
                                        ▼
                              ┌────────────────────┐
                              │ MLB Stats API       │
                              │ statsapi.mlb.com    │
                              │ (외부, 무료, 비공식)   │
                              └────────────────────┘
```

## 2. 기술 스택 — 결정 근거 포함

### 2.1 백엔드

- **Python 3.12 + FastAPI 0.110+**
  - 사유: 본인 강점, MLB-StatsAPI 래퍼 사용 가능, Pydantic v2의 타입 안전성, OpenAPI 문서 자동 생성
- **SQLAlchemy 2.0 + Alembic**
  - 사유: 표준, 마이그레이션 관리 필수
- **MLB-StatsAPI** (toddrob/MLB-StatsAPI)
  - 사유: 가장 안정적이고 활발한 비공식 래퍼. 단, 응답이 deep-nested라 자체 변환 레이어 필요.
- **APScheduler** (in-proc) 또는 **GitHub Actions cron** (out-of-proc)
  - 결정: **GitHub Actions cron** 권장 — 백엔드 단일 프로세스에 스케줄러를 두면 호스팅 재시작/콜드스타트에 잡 유실 위험. 외부 cron 분리가 안전
- **httpx** (외부 HTTP 호출용, 비동기)
- **structlog** + **Sentry SDK** (관측 가능성)

### 2.2 프론트엔드

- **Next.js 14 App Router + TypeScript (strict)**
  - 사유: 처음 배워도 자료 가장 많음. SSR/CSR 모두 학습. Vercel 배포 0설정.
- **Tailwind CSS + shadcn/ui + lucide-react**
  - 사유: shadcn/ui로 디자인 시간 절약, 모던 룩 보장
- **TanStack Query v5**
  - 사유: API 캐싱·리프레시·에러 처리. SWR보다 기능 풍부.
- **Recharts**
  - 사유: 학습 곡선 낮음, React 친화적
- **Zod**: 클라이언트 측 응답 스키마 검증 (옵션)

### 2.3 인프라

| 구성요소 | 서비스 | 무료 한도 |
|---|---|---|
| 프론트엔드 호스팅 | Vercel | 충분 |
| 백엔드 호스팅 | Northflank | Sandbox: always-on 2 services + 1 database, US Central region (Sandbox plan은 EU/US만 선택 가능), 영구 무료 |
| DB | Supabase | 500MB, 2개 프로젝트 |
| 에러 추적 | Sentry | 5k events/month |
| 도메인 (옵션) | Cloudflare | $10/year .com |
| Cron | GitHub Actions | 무료 (퍼블릭 레포) |

## 3. 데이터 모델

```sql
-- 선수 마스터
CREATE TABLE players (
  id              BIGINT PRIMARY KEY,           -- MLB 선수 ID 그대로 사용
  full_name_en    TEXT NOT NULL,
  full_name_ko    TEXT NOT NULL,                -- 수동 매핑 (김혜성, 이정후, ...)
  position        TEXT NOT NULL,                -- 'P', 'IF', 'OF', 'C', ...
  player_type     TEXT NOT NULL,                -- 'batter' | 'pitcher' | 'two_way'
  current_team_id BIGINT,
  current_level   TEXT,                         -- 'MLB' | 'AAA' | 'AA' | 'A+' | 'A'
  is_active       BOOLEAN DEFAULT true,
  birth_date      DATE,
  bats            CHAR(1),                      -- 'L' | 'R' | 'S'
  throws          CHAR(1),
  created_at      TIMESTAMPTZ DEFAULT now(),
  updated_at      TIMESTAMPTZ DEFAULT now()
);

-- 팀 마스터 (정규화)
CREATE TABLE teams (
  id          BIGINT PRIMARY KEY,
  name        TEXT NOT NULL,
  abbrev      TEXT NOT NULL,
  league      TEXT,                              -- 'AL' | 'NL' | 'MiLB'
  level       TEXT
);

-- 시즌 누적 스탯 (선수×시즌 1건)
CREATE TABLE season_stats (
  player_id    BIGINT REFERENCES players(id),
  season       INT,
  group_name   TEXT,                             -- 'hitting' | 'pitching' | 'fielding'
  stats        JSONB NOT NULL,                   -- 유연성 위해 JSONB 사용
  fetched_at   TIMESTAMPTZ DEFAULT now(),
  PRIMARY KEY (player_id, season, group_name)
);

-- 경기별 박스스코어 (선수×경기 1건)
CREATE TABLE game_logs (
  player_id   BIGINT REFERENCES players(id),
  game_id     BIGINT,
  game_date   DATE NOT NULL,
  opponent_id BIGINT,
  is_home     BOOLEAN,
  group_name  TEXT,                              -- 'hitting' | 'pitching'
  stats       JSONB NOT NULL,                    -- AB, H, HR, RBI, ... or IP, ER, K, ...
  fetched_at  TIMESTAMPTZ DEFAULT now(),
  PRIMARY KEY (player_id, game_id, group_name)
);

CREATE INDEX idx_game_logs_date ON game_logs (game_date DESC);
CREATE INDEX idx_game_logs_player_date ON game_logs (player_id, game_date DESC);

-- ETL 실행 로그 (관측 가능성)
CREATE TABLE etl_runs (
  id          BIGSERIAL PRIMARY KEY,
  job_name    TEXT NOT NULL,                     -- 'daily_games' | 'season_stats' | 'roster_sync'
  started_at  TIMESTAMPTZ NOT NULL,
  finished_at TIMESTAMPTZ,
  status      TEXT NOT NULL,                     -- 'running' | 'success' | 'failed'
  error       TEXT,
  meta        JSONB
);
```

**왜 JSONB?** MLB API의 스탯 필드가 50개 이상이고 자주 추가됨. 모든 컬럼을 정규화하면 마이그레이션 부담. 대신 자주 조회하는 핵심 스탯은 generated column으로 뽑아낼 수 있음 (예: `(stats->>'avg')::numeric`).

## 4. API 계약 (Backend)

베이스: `https://api.korean-mlb.example.com/api/v1`

| Method | Path | 설명 | 응답 예 (요약) |
|---|---|---|---|
| GET | `/players` | 한국인 선수 목록 (활성) | `[{id, name_ko, team, level, today_summary}]` |
| GET | `/players/:id` | 선수 상세 | `{...player, season_stats, recent_games}` |
| GET | `/players/:id/games?since=YYYY-MM-DD` | 경기 로그 | `[{game_date, opponent, stats}]` |
| GET | `/dashboard/today` | 메인 대시보드 페이로드 (집계) | `{date, players: [...with_today]}` |
| GET | `/health` | 헬스체크 | `{status, db, last_etl_run}` |

OpenAPI는 FastAPI가 `/docs`에서 자동 생성. 프론트 측 fetch 함수는 `openapi-typescript`로 타입 자동 생성.

## 5. 데이터 수집 파이프라인 (ETL)

### 5.1 잡 정의

| 잡 이름 | 주기 | 대상 | 책임 |
|---|---|---|---|
| `roster_sync` | 매일 1회 (KST 05:00) | 한국인 선수 명단 | 신규 선수 발견·은퇴 처리 |
| `daily_games` | 매일 2회 (KST 12:00, 15:00) | 어제 경기(미국 시간) | game_logs 추가/업데이트 |
| `season_stats` | 매일 1회 (KST 15:00) | 활성 선수 시즌 누적 | season_stats 갱신 |

### 5.2 실행 환경

**GitHub Actions cron 사용**:
- 장점: 별도 인프라 불필요. 실패 시 GitHub 이슈 자동 생성. 무료.
- 백엔드 컨테이너에 `python -m app.jobs.run --job daily_games` 형태로 명령 실행
- 워크플로우는 잡 전용 짧은 Python 스크립트를 Actions runner에서 직접 실행 (DB에 직접 쓰기). 백엔드 컨테이너 SSH 의존성 없음

### 5.3 멱등성

모든 잡은 멱등(idempotent)으로 설계. `UPSERT (ON CONFLICT ... DO UPDATE)` 사용.

## 6. 캐싱 전략

| 레이어 | 무엇 | TTL | 이유 |
|---|---|---|---|
| Next.js | 페이지 (ISR) | 5분 | 메인 대시보드 |
| TanStack Query | API 응답 | 5분 | 클라이언트 측 |
| FastAPI (메모리) | MLB API 직접 응답 | 60초 | 동일 요청 폭주 방지 |
| DB | 데이터 그 자체 | n/a | ETL이 갱신 |

원칙: **MLB Stats API를 사용자 요청 경로에서 직접 호출하지 않는다.** 항상 DB가 SoT.

## 7. 폴더 구조

```
korean-mlb-tracker/
├── README.md
├── CLAUDE.md
├── docs/
│   ├── PRD.md
│   ├── TECH_SPEC.md
│   └── ROADMAP.md
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                  # FastAPI entrypoint
│   │   ├── api/
│   │   │   ├── deps.py              # DI (DB session 등)
│   │   │   └── v1/
│   │   │       ├── players.py
│   │   │       ├── dashboard.py
│   │   │       └── health.py
│   │   ├── core/
│   │   │   ├── config.py            # pydantic-settings
│   │   │   ├── logging.py
│   │   │   └── sentry.py
│   │   ├── db/
│   │   │   ├── base.py
│   │   │   ├── session.py
│   │   │   └── models.py
│   │   ├── schemas/                 # Pydantic DTOs
│   │   │   ├── player.py
│   │   │   └── game.py
│   │   ├── services/
│   │   │   ├── mlb_client.py        # MLB Stats API 래퍼
│   │   │   ├── player_service.py
│   │   │   └── stats_transformer.py # JSON → 우리 스키마
│   │   └── jobs/
│   │       ├── run.py               # python -m app.jobs.run --job=daily_games
│   │       ├── roster_sync.py
│   │       ├── daily_games.py
│   │       └── season_stats.py
│   ├── alembic/                     # 마이그레이션
│   ├── tests/
│   │   ├── unit/
│   │   ├── integration/
│   │   └── fixtures/                # MLB API 응답 모의 (snapshots)
│   ├── pyproject.toml
│   └── Dockerfile
│
├── frontend/
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx                 # 메인 대시보드
│   │   ├── players/[id]/page.tsx
│   │   └── minor-league/page.tsx
│   ├── components/
│   │   ├── ui/                      # shadcn 컴포넌트
│   │   ├── PlayerCard.tsx
│   │   ├── StatsTable.tsx
│   │   └── RecentGamesChart.tsx
│   ├── lib/
│   │   ├── api.ts                   # fetch wrapper
│   │   ├── types.ts                 # openapi 생성 타입
│   │   └── queries.ts               # TanStack Query hooks
│   ├── public/
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.ts
│   └── next.config.mjs
│
└── .github/
    └── workflows/
        ├── backend-ci.yml           # lint + test
        ├── frontend-ci.yml          # lint + build + test
        ├── deploy-backend.yml       # main 머지 시 Northflank 자동 배포 (GitHub auto-deploy)
        ├── deploy-frontend.yml      # main 머지 시 Vercel은 자동
        └── cron-etl.yml             # 스케줄 잡
```

## 8. 환경 변수

### 백엔드 (.env)
```
DATABASE_URL=postgresql+asyncpg://...
SENTRY_DSN=
LOG_LEVEL=INFO
MLB_API_BASE=https://statsapi.mlb.com/api/v1
KOREAN_PLAYER_IDS=672275,808967,673490,672356,808982  # 시드 데이터, 점진 자동화
ALLOWED_ORIGINS=https://korean-mlb.example.com
```

### 프론트엔드 (.env.local)
```
NEXT_PUBLIC_API_BASE_URL=https://api.korean-mlb.example.com
NEXT_PUBLIC_SENTRY_DSN=
```

## 9. 보안 & 운영

- **CORS**: 백엔드는 화이트리스트된 오리진만 허용
- **Rate limiting**: slowapi로 IP당 60req/min
- **시크릿**: Fly secrets / Vercel env, 절대 커밋 금지
- **DB 접근**: Supabase 풀러(Pgbouncer) 사용
- **모니터링 알람**:
  - Sentry: 새 에러 발생 시 Discord webhook
  - ETL 실패: GitHub Actions 실패 → 자동 이슈 생성

## 10. 테스트 전략

| 레이어 | 도구 | 커버리지 목표 |
|---|---|---|
| 백엔드 단위 | pytest | 70% (services, transformer 중심) |
| 백엔드 통합 | pytest + testcontainers-postgres | 핵심 엔드포인트 |
| MLB API 응답 변환 | snapshot test (저장된 JSON 사용) | 100% |
| 프론트 단위 | Vitest + React Testing Library | 주요 컴포넌트만 |
| E2E | Playwright (선택) | 메인 시나리오 1개 |

## 11. 결정 기록 (ADR 요약)

| # | 결정 | 사유 |
|---|---|---|
| 1 | 백엔드/프론트 분리 (모놀리식 Next.js 아님) | 백엔드 어필 + 잡 분리 |
| 2 | DB에 캐싱, 사용자→MLB API 직접 호출 없음 | 비공식 API 안정성 + 응답 속도 |
| 3 | JSONB로 스탯 저장 | 스키마 변화 대응 |
| 4 | GitHub Actions cron (vs in-proc) | 호스팅 콜드스타트/재시작과 ETL 잡 결합 분리 |
| 5 | shadcn/ui (vs MUI/Chakra) | 모던 룩 + 코드 컨트롤 |
| 6 | Fly.io → Northflank (백엔드 호스팅) | Fly 무료 정책이 trial 후 유료 전환. Northflank Sandbox는 영구 무료 + always-on. 자세히는 `docs/adr/0001-deploy-northflank.md` |
