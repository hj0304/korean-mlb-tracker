# ADR-0001: 백엔드 호스팅 — Fly.io → Northflank

- **Date**: 2026-05-23
- **Status**: Accepted
- **Supersedes**: 초기 TECH_SPEC §2.3 결정 (Fly.io)

## Context

초기 TECH_SPEC은 백엔드 호스팅으로 Fly.io 무료 `shared-cpu-1x 256MB 3대` 한도를 가정했다. S0-04(첫 배포)를 진행하면서 두 가지가 확인됨:

1. Fly.io는 무료 plan을 폐지했고, 신규 계정은 1개월 trial 이후 유료 plan으로 자동 전환된다.
2. 본 프로젝트는 포트폴리오용이며 항구적 $0 운영이 요구사항이다.

대안 비교:

| 옵션 | 영구 무료 | Sleep | Asia region | 비고 |
|---|---|---|---|---|
| Fly.io | ❌ (1개월 trial 후 유료) | n/a | nrt (Tokyo) | 폐기 |
| Render Free | ✅ | ⚠ 15분 idle 후 sleep, ~50초 cold start | sin (Singapore) | PRD §6 성능 위배 가능 |
| Northflank Sandbox | ✅ | ❌ always-on | EU West / US (Asia East는 유료 plan 전용) | **채택** |

## Decision

**Northflank Sandbox tier**를 백엔드 호스팅으로 사용한다.

- Region: `US Central` (Sandbox plan에선 Asia East가 선택 불가 — EU West와 US만 풀림. 한국에서 RTT ~180ms 예상)
- Service type: Combined service (Build + Deploy)
- Source: GitHub `hj0304/korean-mlb-tracker`, branch `main`, auto-deploy ON
- Build: Dockerfile, build context = `/backend`
- Internal port: 8000 (HTTP/1, Public)
- Compute: 가장 작은 Sandbox plan

## Consequences

**Positive**
- 영구 $0 (Sandbox 한도 내)
- Sleep 없음 → cold start 없음, PRD §6 API <300ms 만족 가능
- Docker 기반 — 다른 호스팅으로 마이그레이션 부담 낮음

**Negative**
- Fly.io 대비 덜 알려진 플랫폼 — README/면접에서 "왜 Northflank?" 설명이 필요 (이 ADR이 그 답)
- Sandbox 한도(always-on 2 services + 1 database)를 초과하면 유료. 현재는 1 service만 사용
- 실제 region은 US Central — 한국에서 warm RTT 실측 ~210ms (`/health` 기준, 3회 측정 후 2·3회차 평균). 첫 호출은 TLS handshake로 ~1.3s. PRD §6 (<300ms)는 warm 상태에서 만족

## Operational Notes

- TECH_SPEC §11 ADR #4 ("GitHub Actions cron")는 여전히 유효. 호스팅이 바뀌어도 ETL을 백엔드 프로세스에 결합하지 않는 원칙은 동일
- `backend/fly.toml`은 본 ADR과 함께 제거됨
- Northflank IaC(yaml) 파일 도입 여부는 첫 배포 후 재평가
