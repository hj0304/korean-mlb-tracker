# ADR-0007: 스탯을 리그 레벨 차원으로 분리

- **Date**: 2026-06-30
- **Status**: Accepted
- **Related**: PR #67, #68, #72 / ROADMAP S2-15, S2-16

## Context

한 선수가 한 시즌에 여러 레벨을 뛴다(콜업·강등: 예) 2026 김혜성 MLB+AAA).
초기 `season_stats` PK는 `(player_id, season, group_name)`이라 한 시즌에 한 행만
가능 → 트랜스포머가 `gamesPlayed`가 가장 많은 레벨 하나만 남기고 **나머지 레벨을
버렸다**. `game_logs`엔 레벨 정보가 아예 없었다.

## Decision

레벨을 1급 데이터 차원으로 승격한다.

- `season_stats` PK에 **`level` 추가** → `(player_id, season, group_name, level)`.
  `transform_year_by_year`가 `(시즌, 그룹, 레벨)`별 1행을 방출(레벨 내에선
  gamesPlayed 최다 split = 다팀 합산 split 우선).
- `game_logs`에 **nullable `level`** 추가. `daily_games`는 게임을 가져온 스케줄의
  sportId로 레벨을 안다.
- 부수: `season_stats.team_id`(nullable)도 추가해 연도별 소속팀을 기록(다팀 시즌은
  combined split이라 null → UI "여러 팀"). (S2-16)
- 프론트는 상세 페이지에 **레벨 탭**을 두고 요약·통산·경기·차트를 선택 레벨로 필터.

## Consequences

**Positive**
- AAA/MLB를 오가는 유망주의 레벨별 성적을 정확히 보존·표시.
- 레벨이 컬럼이라 레벨별 캐시 키 분리(S2-02)·필터가 자연스럽다.

**Negative**
- PK 변경 마이그레이션 + 라이브 재구축 필요. **교훈**: PK를 바꾸면 ETL의
  `on_conflict_do_update(index_elements=...)`도 새 PK와 정확히 일치시켜야 한다
  (안 그러면 "no unique constraint matching the ON CONFLICT specification"으로
  잡이 죽음). 통합 테스트는 `create_all`이라 이걸 못 잡고, 실 마이그레이션 DB에서만
  드러난다.
- `level`은 `stats` JSONB가 아니라 행 컬럼 — 스냅샷 테스트를 함께 갱신.
