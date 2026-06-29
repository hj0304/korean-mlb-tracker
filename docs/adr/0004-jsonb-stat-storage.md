# ADR-0004: 스탯을 JSONB로 저장 (정규화 컬럼 아님)

- **Date**: 2026-06-30
- **Status**: Accepted
- **Related**: TECH_SPEC §3 (데이터 모델) / ROADMAP S1-01

## Context

`season_stats`와 `game_logs`가 담아야 하는 MLB 스탯 필드는 그룹별로 50개가 넘고
(타격: avg/obp/slg/ops/babip/…, 투구: era/whip/fip/inheritedRunners/…), MLB
Stats API가 시간이 지나며 필드를 더 추가한다. 또 타자/투수/(잠재적으로 수비)에
따라 키 집합이 다르다.

선택지:

| 옵션 | 마이그레이션 부담 | 쿼리/집계 | 새 필드 대응 |
|---|---|---|---|
| 와이드 정규화 컬럼 | 필드마다 컬럼+마이그레이션 | SQL 친화적 | 필드 추가마다 스키마 변경 |
| **JSONB 한 컬럼(`stats`)** | 없음 | `stats->>'avg'` 등 | **무중단** |

## Decision

스탯 본문은 **`stats JSONB`** 한 컬럼에 API가 준 그대로 저장한다. 행을 식별하는
차원(player_id, season, group_name, level, game_id, opponent_id, game_date 등)만
실제 컬럼으로 둔다.

- 프론트는 표시할 키를 `StatConfig`로 골라 `stats[key]`를 읽는다 — 백엔드 스키마
  변경 없이 노출 스탯을 조정.
- 실 쿼리 패턴이 생기면 generated column(`(stats->>'avg')::numeric`)으로 일부만
  승격할 수 있다(아직 불필요 — CLAUDE.md "Things NOT To Do").

## Consequences

**Positive**
- API가 새 필드를 추가해도 마이그레이션·코드 변경 없이 그대로 수용.
- 타자/투수의 상이한 키 집합을 한 테이블에서 자연스럽게 처리.

**Negative**
- DB 레벨 집계/정렬이 제한적(앱에서 파싱). 단 데이터는 일 1회 ETL로 갱신되고
  선수 수가 적어(≈19) 앱-측 처리로 충분.
- 타입 안정성이 약함(전부 문자열·동적 키) → 트랜스포머 스냅샷 테스트로 방어.
