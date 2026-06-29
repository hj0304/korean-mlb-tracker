# ADR-0005: 읽기 엔드포인트에 인프로세스 TTL 캐시 (Redis 아님)

- **Date**: 2026-06-30
- **Status**: Accepted
- **Related**: ROADMAP S2-05 / TECH_SPEC §6 (캐싱)

## Context

데이터는 하루 1회 ETL로만 바뀌는데, 매 요청마다 Supabase로 왕복하면 느리다.
근본 지연 요인은 백엔드 리전(US Central) ↔ Supabase(Seoul)의 물리적 거리라,
읽기 경로의 DB 왕복을 줄이는 게 효과적이다.

선택지: (a) 캐시 없음, (b) Redis 등 외부 캐시, (c) 프로세스 내 메모리 TTL 캐시.

## Decision

읽기 전용 엔드포인트(players/dashboard/games)에 **프로세스 내 TTL 캐시(5분)**를
두고, 응답에 `Cache-Control: public, max-age=300`을 함께 보낸다(브라우저/CDN도
캐시).

- 데이터가 일 1회만 갱신되므로 5분 staleness는 무해.
- Redis를 추가하지 않음 — 인프라/비용/운영 부담 대비 이득이 작다(단일 백엔드
  인스턴스, 소규모 트래픽).

## Consequences

**Positive**
- DB 왕복 제거로 응답 빨라짐, 외부 의존성 0.
- `Cache-Control`로 엣지/브라우저 캐시까지 활용.

**Negative**
- 인스턴스가 여러 개로 스케일되면 캐시가 인스턴스별로 분리됨(현재 단일이라 무관;
  스케일아웃 시 공유 캐시로 재검토).
- 테스트 간 캐시가 새지 않도록 `conftest`에서 매 테스트 캐시를 비운다(S2-13).
- ETL 직후 최대 5분간 옛 응답이 보일 수 있음 — 운영 중 백필 검증 시 이 점을 고려.
