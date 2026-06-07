# Roadmap — Korean MLB Tracker

> **상태**: Draft v1.0 · **목표 출시(v1.0)**: 5~6주 후 · **관련 문서**: PRD.md, TECH_SPEC.md

## 진행 원칙

1. **End-to-end first**: 선수 1명에 대해서라도 DB → API → UI → 배포까지 작동시키고 그 다음에 확장
2. **데모 가능한 작은 단위**: 각 Sprint 종료 시점에 누군가에게 보여줄 수 있어야 함
3. **티켓 단위는 0.5~1일**: 너무 큰 티켓은 진행 상황이 안 보임
4. **README 우선 갱신**: 채용 담당자가 보는 첫 페이지

---

## Sprint 0 — 기초 셋업 (목표: 3~5일)

**Definition of Done**: `git push` 하면 백엔드·프론트엔드 둘 다 CI가 돌고 배포 환경에 "Hello World" 페이지가 뜬다.

### 작업

- [x] **S0-01** GitHub 레포 생성, 라이선스(MIT), `.gitignore`
- [x] **S0-02** 모노레포 폴더 구조 생성 (backend/, frontend/, docs/)
- [x] **S0-03** `backend`: `pyproject.toml` (uv 또는 poetry), FastAPI 최소 앱, `/health` 엔드포인트
- [x] **S0-04** `backend`: Dockerfile, Northflank 첫 배포
- [x] **S0-05** `backend`: GitHub Actions — lint(ruff) + test(pytest, 빈 테스트 1개)
- [x] **S0-06** `frontend`: `create-next-app@latest --typescript --tailwind --app`, shadcn/ui init
- [x] **S0-07** `frontend`: Vercel 연결, 자동 배포 확인
- [x] **S0-08** `frontend`: GitHub Actions — lint + typecheck + build
- [x] **S0-09** `db`: Supabase 프로젝트 생성, 연결 문자열 확보
- [x] **S0-10** `db`: Alembic 셋업, 빈 첫 마이그레이션
- [x] **S0-11** Sentry 프로젝트 생성 (백/프 둘 다), DSN 환경변수 연결
- [x] **S0-12** `README.md` 초안 (스크린샷 자리만 비워두기), 배지(CI, Vercel, license)

**산출물**: 배포된 도메인 2개 (`api-staging.fly.dev`, `[name].vercel.app`), 그린 CI 배지.

---

## Sprint 1 — MVP: 김혜성 한 명, end-to-end (목표: 5~7일)

**Definition of Done**: 누군가가 사이트에 들어가서 김혜성(또는 임의의 1명) 카드를 보고 클릭하면 시즌 누적 + 어제 경기를 본다. 데이터는 실제 MLB API에서 나오고, ETL이 매일 돈다.

### 작업

#### 백엔드
- [x] **S1-01** DB 모델: `players`, `teams`, `season_stats`, `game_logs`, `etl_runs`
- [x] **S1-02** Alembic 마이그레이션 작성·적용
- [x] **S1-03** `services/mlb_client.py`: MLB Stats API 호출 함수 (httpx). 일단 사용할 엔드포인트 3개만:
  - `/people/{id}` (선수 정보)
  - `/people/{id}/stats?stats=season&group=hitting,pitching&season=2026`
  - `/schedule?sportId=1&teamId=X&date=YYYY-MM-DD` + `/game/{gamePk}/boxscore`
- [x] **S1-04** `services/stats_transformer.py`: MLB JSON → 우리 스키마. **snapshot test** 셋업.
- [x] **S1-05** `jobs/roster_sync.py`: 시드 ID 5명을 DB에 upsert
- [x] **S1-06** `jobs/season_stats.py`: 시즌 스탯 동기화
- [x] **S1-07** `jobs/daily_games.py`: 어제 경기 동기화 (한 선수 먼저, 그 다음 5명)
- [x] **S1-08** API: `GET /api/v1/players` (목록), `GET /api/v1/players/{id}` (상세)
- [x] **S1-09** API: `GET /api/v1/players/{id}/games?since=` (경기 로그)
- [x] **S1-10** pytest: transformer 단위 테스트, API 통합 테스트 1개

#### 프론트엔드
- [x] **S1-11** `lib/api.ts`: 백엔드 fetch wrapper, 에러 처리
- [x] **S1-12** `openapi-typescript`로 타입 자동 생성 (npm script)
- [x] **S1-13** TanStack Query Provider, 글로벌 에러 바운더리
- [x] **S1-14** `app/page.tsx`: 선수 카드 리스트 (PlayerCard 컴포넌트)
- [x] **S1-15** `app/players/[id]/page.tsx`: 선수 상세 (시즌 + 최근 경기 테이블)
- [x] **S1-16** 로딩 스켈레톤 + 에러 상태 UI
- [x] **S1-17** 모바일 반응형 확인 (Chrome devtools 375px)

#### 운영
- [x] **S1-18** GitHub Actions cron: `daily_games` 매일 KST 12시 실행
- [ ] **S1-19** README에 첫 스크린샷 추가, "How to run locally" 섹션
- [ ] **S1-20** 본인 도그푸딩: 3일 연속 사용 후 발견된 문제 이슈로 정리

**산출물**: 작동하는 사이트. 김혜성 카드 클릭 → 어제 경기와 시즌 스탯이 뜸. 첫 데모.

---

## Sprint 2 — 확장: 전체 선수 + MiLB + 차트 (목표: 5~7일)

**Definition of Done**: MLB 한국인 선수 전원 + MiLB 한국인 선수 일부가 표시되고, 최근 10경기 추이 차트가 보인다.

### 작업

#### 백엔드
- [x] **S2-01** MiLB 데이터: sportId 11/12/13/14 호출 추가. MiLB 한국인 선수 명단 수동 시드 (예: 5~10명) — 3분할(a 로스터+레벨 / b 시즌스탯 / c 일일경기)로 진행, 루키(16) 포함
- [ ] **S2-02** `players.current_level` 활용한 필터 API: `GET /api/v1/players?level=MLB|AAA|AA`
- [ ] **S2-03** `GET /api/v1/dashboard/today`: 메인 대시보드 집계 (오늘자 경기 결과 포함)
- [ ] **S2-04** 최근 N경기 조회 최적화 (인덱스 점검)
- [ ] **S2-05** 슬로우 API 식별 → 캐싱 추가 (functools.lru_cache 또는 cache decorator)

#### 프론트엔드
- [ ] **S2-06** 탭/필터: "MLB | AAA | AA"
- [ ] **S2-07** `RecentGamesChart.tsx`: Recharts로 최근 10경기 OPS/ERA 추이
- [x] **S2-08** 타자/투수 카드 디자인 분리 (조건부 렌더) — 상세 페이지를 player_type별 config로 분기(투수: ERA/WHIP/K9/이닝/승패세홀 등). 목록 카드는 스탯 미표시라 분기 불필요
- [ ] **S2-09** 다크 모드 토글 (next-themes)
- [ ] **S2-10** OG 이미지, 메타데이터 (Next metadata API)
- [ ] **S2-11** 빈 상태 (오늘 경기 없음) UI

#### 품질
- [ ] **S2-12** Lighthouse 측정 → 90+ 목표 (이미지 최적화, 폰트 preload 등)
- [ ] **S2-13** 백엔드 통합 테스트 추가 (전체 엔드포인트)
- [ ] **S2-14** Sentry 첫 알람 셋업 (Discord 또는 이메일)

**산출물**: 거의 완성된 사이트. 차트가 멋있게 들어가서 스크린샷이 화려해짐.

---

## Sprint 3 — 폴리시 & 출시 (목표: 3~5일)

**Definition of Done**: README가 채용 담당자 기준으로 통과한다. 도메인이 박혀 있고, 30일 무중단 운영을 시작할 준비가 됐다.

### 작업

- [ ] **S3-01** 커스텀 도메인 연결 (Cloudflare 또는 Vercel 무료 서브도메인)
- [ ] **S3-02** README 본격 작성:
  - 헤더 이미지/로고
  - 라이브 데모 링크, 스크린샷 3장 (데스크탑/모바일/다크)
  - **아키텍처 다이어그램** (Excalidraw → PNG)
  - 기술 스택 배지
  - Local dev 가이드
  - **결정 기록** 섹션 (왜 이 스택? 왜 JSONB?)
  - 향후 계획
- [ ] **S3-03** 백엔드 OpenAPI 문서를 GitHub Pages 또는 redoc-static으로 호스팅, README에 링크
- [ ] **S3-04** ETL 실패 시 GitHub 이슈 자동 생성 워크플로우
- [ ] **S3-05** Vercel Analytics 또는 Plausible 설정
- [ ] **S3-06** 작성한 ADR(아키텍처 결정 기록) 5개 정도를 `docs/adr/`에 별도 정리
- [ ] **S3-07** 회고 노트 `docs/RETRO.md`: 무엇이 어려웠고 무엇을 배웠는지 (포트폴리오 인터뷰 무기)
- [ ] **S3-08** 한국 야구 커뮤니티 1곳에 공유 (도그푸딩 외부 사용자 첫 확보)

**산출물**: 이력서에 URL 박을 수 있는 상태. 면접에서 화면 공유로 보여줄 수 있는 사이트.

---

## Sprint 4+ — P1 이후 (출시 후, 시즌 종료까지)

P1/P2 기능 중 우선순위 높은 것 1~2개씩. 시즌 데이터로 학습한 인사이트를 README에 누적.

후보:
- 알림 기능 (홈런/완봉 시 Web Push)
- 선수 간 비교 페이지
- 월별 추이 그래프
- 영문 지원
- 세이버메트릭스(고급 지표) 표시 — MLB Stats API의 `stats=sabermetrics`(WAR·wOBA·wRAA 등) / Statcast expected(xBA·xSLG·xwOBA 등) 타입을 `mlb_client`에 추가 수집 → transformer/스키마/상세 페이지 확장. 실제 응답을 fixture로 받아 제공 필드부터 확인 (PRD F-205)
- 상세 페이지 폴리시 (재디자인 3종 — 요약그리드/추이차트/통산행 — 안착 후): 요약 그리드/테이블에 **추가 세부 스탯** 더 노출, 디자인 마감(대표 스탯 강조색 등 시각 디테일). 디자인 확정은 기능 완성 후 일괄 검토

---

## 진행 추적

| Sprint | 시작 | 종료 (목표) | 종료 (실제) | 비고 |
|---|---|---|---|---|
| Sprint 0 | | | | |
| Sprint 1 | | | | |
| Sprint 2 | | | | |
| Sprint 3 | | | | |

## 리스크 & 완화

| 리스크 | 영향 | 완화 |
|---|---|---|
| MLB Stats API 갑작스러운 변경 | 높음 | snapshot test로 빠르게 감지, 백업 소스(baseball-reference 스크래핑) 가능성 조사 |
| 백엔드 호스팅 콜드스타트/장애로 ETL 누락 | 중간 | GitHub Actions cron으로 외부 트리거 (Northflank Sandbox는 sleep 없음) |
| 처음 배우는 프론트엔드 학습 곡선 | 중간 | shadcn/ui 적극 활용, 욕심 부리지 않기 (애니메이션 등은 P2) |
| 스코프 크리프 | 높음 | PRD의 비목표 섹션 자주 본다. P2는 v1 출시 전에 손대지 않는다. |
