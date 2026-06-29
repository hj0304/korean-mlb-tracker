# ADR-0002: `daily_games` — 팀 기준이 아닌 날짜 기준 조회

- **Date**: 2026-06-03
- **Status**: Accepted (부분 갱신 — 아래 참고)
- **Related**: ROADMAP S1-07, S2-01 / TECH_SPEC §8 (ETL)

> **갱신 노트**: 예고대로 S2-01(MiLB)에서 "그날 전 경기 fetch"는 호출량 때문에
> **팀 기준 필터로 전환**됐다(`game_team_ids & team_ids`). 그 team_ids는 현재
> `current_team_id` ∪ `season_stats.team_id`(시즌 중 뛴 모든 팀)로, 트레이드/콜업에
> 견고하게 보강됨(PR #74). 타임존 단순화 노트는 **ADR-0006**(KST 날짜)이 대체한다.

## Context

`daily_games` 잡은 특정 날짜에 추적 선수들이 출전한 **완료된 경기**를 `game_logs`에 적재해야 한다.

ROADMAP S1-03의 엔드포인트 노트는 `/schedule?sportId=1&teamId=X&date=YYYY-MM-DD` + `/game/{gamePk}/boxscore`를 전제했다 — 즉 **선수의 소속 팀(teamId)** 으로 그날 경기를 찾는 "팀 기준" 흐름이다.

그러나 `roster_sync`(S1-05)는 `players.current_team_id`를 의도적으로 비워둔 채 **S2-01로 미뤘다**(MiLB 레벨 처리와 함께). 따라서 Sprint 1 동안 `players` 테이블에는 team_id가 없어, 팀 기준 조회를 DB만으로는 할 수 없다.

대안 비교:

| 옵션 | team_id 의존 | API 호출량(1일) | 트레이드/콜업 견고성 | 비고 |
|---|---|---|---|---|
| 팀 기준 | `/people/{id}`로 currentTeam 실시간 조회 → 팀별 schedule | 선수당 person + schedule + boxscore | 옵션/트레이드 시 어긋날 수 있음 | ROADMAP 엔드포인트와 일치하나 S2-01 결합 |
| **날짜 기준** | **없음** | schedule 1회 + 그날 MLB 박스스코어 전부(~15) | 견고(팀과 무관) | **채택** |

## Decision

**날짜 기준**으로 구현한다.

- `mlb_client.get_schedule`의 `team_id`를 optional로 완화 → `sportId + date`만으로 그날 전체 MLB 경기를 조회.
- 응답에서 `status.abstractGameState == "Final"` 인 경기만 추출(`extract_completed_games`) — **완료 경기만**(PRD 비목표: 라이브 중계 안 함).
- 해당 gamePk들의 박스스코어를 `asyncio.TaskGroup`으로 병렬 fetch.
- `transform_game_log`이 각 박스스코어에서 추적 선수(player_id 일치)만 매칭 → 출전 안 한 경기는 `[]`.
- `run.py`에 `--date` 인자 추가(기본값: 어제). 기본 타임존 처리는 단순화했고, 정확한 US 경기 날짜 매핑은 cron(S1-18)에서 명시 `--date`로 넘기는 것을 권장.

## Consequences

**Positive**
- `current_team_id`(S2-01)에 **의존하지 않음** → Sprint 1에서 바로 동작.
- 트레이드/콜업/옵션 이동에 견고 — 선수의 "현재 팀"을 알 필요가 없음.
- "완료 경기만" 원칙을 schedule 단계에서 자연스럽게 필터.

**Negative**
- 추적 선수가 없는 경기의 박스스코어까지 그날 ~15개를 전부 fetch(once-daily cron이라 무방).
- **MiLB 확장(S2-01)** 시 sportId 11/12/13/14를 더하면 "그날 전 경기" 접근의 호출량이 레벨마다 커진다 → 그 시점에 팀 기준(또는 선수→레벨/팀 매핑)으로 **재검토 필요**.
- 상대팀이 `game_logs.opponent_id`(팀 ID)로만 남아, 상세 화면에서 팀 이름이 아닌 숫자로 표시됨 → `teams` 테이블 채우는 S2-01에서 해소.

## Operational Notes

- 시그니처 변경: `get_schedule(client, date, team_id=None, sport_id=1)` (기존 `team_id` positional → optional). `test_mlb_client`의 해당 테스트 갱신됨.
- 새 fixture: `tests/fixtures/mlb_responses/schedule_2026-04-06.json`.
- S2-01에서 이 ADR을 재평가하고, 팀 기준 전환이 필요하면 후속 ADR로 supersede.
