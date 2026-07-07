# ADR-0009: 즐겨찾기를 위한 로그인 도입 (Supabase Auth)

- **Date**: 2026-07-07
- **Status**: Accepted
- **Related**: ROADMAP Sprint 4 (S4-01~S4-05) / PRD §3, §5

## Context

사용자가 응원하는 선수만 골라 보는 **즐겨찾기** 기능을 추가하고 싶다. 즐겨찾기가
기기 간에 유지되려면 서버에 사용자 단위로 저장해야 하고, 그러려면 로그인이 필요하다.

PRD §3은 v1.0 스코프 컨트롤을 위해 "회원가입/로그인"을 비목표로 명시했다.
v1.0 출시 목표(선수 성적 조회)는 달성했으므로, v1.1에서 이 비목표를 해제한다.
단, 댓글·좋아요 등 소셜 기능 비목표는 그대로 유지한다 — 로그인의 용도는
**즐겨찾기 저장 하나뿐**이다.

선택지:

1. **비로그인 + localStorage** — 구현 최소지만 기기 간 동기화 불가, 브라우저
   데이터 삭제 시 유실.
2. **자체 auth 구현** (FastAPI + JWT + 비밀번호 저장) — 비밀번호 해싱/재설정/
   세션 관리 전부 직접 운영. 포트폴리오 대비 리스크(보안 사고 표면)가 크다.
3. **Supabase Auth** — DB가 이미 Supabase. OAuth(Google/카카오)와 이메일/비밀번호
   가입을 대시보드 설정으로 제공, 비밀번호를 우리가 저장하지 않음. 프론트는
   `@supabase/supabase-js`로 로그인하고, 백엔드는 Supabase가 발급한 JWT를
   검증만 하면 된다.

## Decision

**Supabase Auth**를 도입한다 (선택지 3).

- 로그인 수단: **Google OAuth + 카카오 OAuth + 이메일/비밀번호**.
- **즐겨찾기는 로그인 필수** — localStorage 게스트 모드는 만들지 않는다(1안 기각).
  동기화·유실 문제를 원천 차단하고 코드 경로를 하나로 유지.
- 백엔드는 요청 헤더의 Supabase JWT를 검증(`SUPABASE_JWT_SECRET`)해 `user_id`를
  얻고, `favorites(user_id, player_id)` 테이블로 저장한다. auth 사용자 테이블은
  Supabase가 관리하는 `auth.users`를 그대로 쓴다.
- 비로그인 사용자 경험은 기존과 동일(전체 조회는 로그인 없이 가능). 랜딩 페이지는
  비로그인 상태에서만 노출.

## Consequences

**Positive**
- 비밀번호를 저장·운영하지 않음. OAuth 연동이 대시보드 설정 수준.
- DB와 auth가 같은 Supabase 프로젝트라 인프라 추가 없음.
- 즐겨찾기 외 개인화 기능(알림 구독 등 P2)이 생겨도 같은 JWT 경로 재사용 가능.

**Negative**
- Supabase 종속 심화 (이미 DB로 종속돼 있어 한계 비용은 작음).
- Google Cloud Console / Kakao Developers에 OAuth 앱 등록 필요(수동 1회).
- 백엔드에 JWT 검증 의존성(`PyJWT`)과 인증 미들웨어 코드 경로가 추가됨.
