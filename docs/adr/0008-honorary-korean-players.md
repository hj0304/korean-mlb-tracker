# ADR-0008: "명예 한국인"을 별도 플래그로 추적

- **Date**: 2026-06-30
- **Status**: Accepted
- **Related**: PR #76, #77 / ROADMAP S2-17 / PRD §1

## Context

한국 출생은 아니나 부모가 한국 국적이라 WBC 등 국제대회에서 대한민국 대표팀으로
뛴 선수들("명예 한국인": 토미 에드먼, 데인 더닝, 셰이 위트컴, 저마이 존스,
라일리 오브라이언)도 추적하고 싶다. 다만 이들은 한국 국적 선수와 **개념적으로 구분**
되어야 한다(앱 이름이 "Korean MLB Tracker"이고 PRD는 한국 국적 + KBO/NPB 제외로
범위를 정의).

선택지: (a) `KOREAN_PLAYERS`에 그냥 합치기(구분 소실), (b) 별도 카테고리로 표시.

## Decision

별도 그룹으로 모델링한다.

- `config.HONORARY_PLAYERS`(MLB id → 한국어명) 시드를 분리하고, `players`에
  **`is_honorary` boolean**(기본 false) 추가. `roster_sync`가
  `KOREAN_PLAYERS ∪ HONORARY_PLAYERS`를 시드하며 플래그를 세팅.
- 수집 파이프라인(roster/daily/season)은 DB의 `players`를 읽으므로, 시드에 추가하면
  경기·시즌 데이터가 기존 선수와 동일하게 흐른다(별도 코드 경로 없음).
- 프론트는 목록에 **전체/한국인/명예 한국인** 필터 축(레벨과 독립) + 카드·상세 배지.

## Consequences

**Positive**
- 한 파이프라인으로 둘 다 처리하되 UI·데이터에서 명확히 구분.
- 향후 다른 분류(예: 교포/혼혈)도 같은 플래그 패턴으로 확장 가능.

**Negative**
- PRD의 "한국인" 범위 정의를 넓혀야 함(주석 추가).
- 명예 선수는 대개 풀타임 MLB/AAA라 시즌 경기 수가 많아 백필 분량이 큼(1회성).
