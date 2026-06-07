# 트러블슈팅 기록 (삽질 로그)

개발하면서 막혔던 문제들을 **증상 → 원인 → 진단 → 해결 → 교훈** 순으로 남긴다.
포트폴리오 인터뷰에서 "어떤 문제를 어떻게 해결했나"를 구체적으로 말하기 위한 자료.

> 공통 교훈 한 줄: **로컬에서 되는데 배포에서 안 되면 거의 항상 "환경(env)·리전·CORS" 셋 중 하나다.**

## 목록

| # | 문제 | 한 줄 요약 | 영역 |
|---|---|---|---|
| [01](01-prod-500-missing-database-url.md) | 배포 API 전체 500 | Northflank에 `DATABASE_URL` env 누락 → `/health`만 살고 DB 엔드포인트 전멸 | 배포/env |
| [02](02-cors-blocked-vercel-origin.md) | 배포 사이트만 "불러오지 못함" | 백엔드 CORS 허용 목록에 Vercel 주소 없음 (로컬은 됨) | 배포/CORS |
| [03](03-stale-season-stats-no-cron.md) | 시즌 스탯이 옛날 값 | `daily_games` cron만 있고 `season_stats` cron이 없어 누적이 멈춤 | ETL |
| [04](04-slow-api-region-and-caching.md) | 첫 로딩이 느림(~2s+스파이크) | 백엔드(US)↔DB(Seoul) 리전 간 왕복 + 캐시 부재 | 성능 |
| [05](05-pitcher-stats-not-rendered.md) | 투수 성적이 안 보임 | 상세 페이지가 타격 스탯만 하드코딩 | 프론트 |
| [06](06-milb-data-collection.md) | MiLB 데이터 수집의 함정 | yearByYear 기본=MLB만, 레벨별 개별 호출·시즌 병합 필요 | 데이터/API |
| [07](07-windows-asyncpg-ssl.md) | 로컬 통합 테스트만 실패 | 한글 사용자명 경로 → asyncpg가 SSL 인증서 로드 실패 | 환경/Windows |
| [08](08-deployed-site-calls-localhost.md) | 배포 사이트가 `localhost:8000` 호출 | Vercel에 `NEXT_PUBLIC_API_BASE_URL` 미설정(빌드타임 env) | 배포/프론트 |

## 형식

각 문서는 아래 골격을 따른다:

```
## 증상      무엇이 어떻게 잘못 보였나
## 원인      실제 근본 원인
## 진단      어떻게 좁혀갔나 (재현/측정/로그)
## 해결      무엇을 바꿨나
## 교훈      다음에 같은 부류를 빨리 잡는 법
```
