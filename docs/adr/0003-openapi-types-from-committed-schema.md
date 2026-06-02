# ADR-0003: 프론트 타입 생성 — 커밋된 OpenAPI 스키마 기반

- **Date**: 2026-06-03
- **Status**: Accepted
- **Related**: ROADMAP S1-12 / TECH_SPEC §6 (OpenAPI → `openapi-typescript`)

## Context

프론트엔드는 백엔드 OpenAPI 문서로부터 `openapi-typescript`로 응답 타입을 자동 생성한다(`npm run gen:types`). 스키마를 도구에 넘기는 방식이 두 가지다:

| 옵션 | 백엔드 실행 필요 | CI/재현성 | 비고 |
|---|---|---|---|
| 라이브 URL | ✅ 서버 + (보통) DB 기동 후 `/openapi.json` 조회 | 서버 의존 | 환경마다 결과 흔들릴 수 있음 |
| **커밋된 파일** | ❌ 없음 | 결정적, 오프라인 | **채택** |

FastAPI의 `app.openapi()`는 라우트 메타데이터만으로 스키마를 만들며 **DB 연결이 필요 없다**(앱 import 시 Settings/엔진을 lazy하게 다루므로 CI에서도 안전).

## Decision

**백엔드 OpenAPI 스키마를 파일로 덤프해 커밋**하고, 그 파일로 타입을 생성한다.

- `backend/openapi.json` ← `app.openapi()` 덤프, 레포에 커밋.
- `frontend/package.json`: `"gen:types": "openapi-typescript ../backend/openapi.json -o lib/api.types.ts"`.
- 생성물 `frontend/lib/api.types.ts`도 커밋. `lib/api.ts`가 친숙한 별칭(`Player`/`PlayerDetail`/`GameLog`/`SeasonStats`)으로 re-export.

## Consequences

**Positive**
- `gen:types`가 **서버/DB 없이** 오프라인·CI에서 동작. 결정적(diff 깔끔).
- 백엔드 스키마가 레포에 박혀 있어 프론트만 체크아웃해도 타입 생성 가능.

**Negative**
- 백엔드 API가 바뀌면 `openapi.json`을 **수동 재생성**해야 함(잊으면 타입 drift). 향후 CI에 drift 체크(재생성 후 diff 비교)를 추가해 완화 가능.

## Operational Notes

- 스키마 재생성(backend 디렉토리에서):
  ```bash
  uv run python -c "import json; from app.main import app; open('openapi.json','w',encoding='utf-8').write(json.dumps(app.openapi(), indent=2, ensure_ascii=False) + '\n')"
  ```
  이후 frontend에서 `npm run gen:types`.
- 반복 빈도가 늘면 위 한 줄을 backend 스크립트(예: `python -m app.openapi_dump`)로 승격 검토.
