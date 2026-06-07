# 01. 배포 API 전체가 500 — Northflank `DATABASE_URL` env 누락

## 증상
- 라이브 사이트에서 선수 데이터가 안 뜸.
- 백엔드 `/health`는 **200 OK** (앱은 살아있음).
- 그런데 `/api/v1/players`, `/players/{id}` 등 **DB를 쓰는 모든 엔드포인트가 500**.
- 처음엔 "이정후 기록이 잘못 들어왔나?"로 의심 → 데이터 문제가 아니었음.

## 원인
프로덕션(Northflank)에 환경변수 `DATABASE_URL`이 **아예 없었다.**
`Settings`(pydantic-settings)가 `database_url`을 필수 필드로 두기 때문에:
- 앱은 부팅됨 → `/health`(DB 안 씀)는 200
- DB 의존성 주입 시점에 `Settings()` 생성 → `ValidationError: database_url Field required` → 500

로컬은 `backend/.env`에 값이 있어 정상. **로컬 OK / 배포 NG**의 전형.

## 진단
1. `/health`(200) vs DB 엔드포인트(500) 대비 → "앱은 살았고 DB 경로만 죽음".
2. 로컬에서 동일 `DATABASE_URL`로 쿼리·직렬화 모두 성공 → 코드/데이터 문제 아님.
3. Northflank **런타임 로그**의 트레이스백 맨 아래 줄:
   `pydantic_core...ValidationError: 1 validation error for Settings / database_url / Field required`.

> 핵심: 500의 진짜 원인은 **트레이스백 마지막 줄**에 있다. 중간 미들웨어 스택만 보고 헤매지 말 것.

## 해결
Northflank 서비스 → Environment variables → `DATABASE_URL` 추가(Supabase asyncpg URL, `backend/.env`와 동일 값) → 재시작.
이 값은 GitHub Actions secret의 동명 변수와는 **별개**다(서로 다른 실행 환경).

## 교훈
- 같은 비밀값이 **로컬 / Northflank / GitHub Actions** 3곳에 따로 존재한다. 한 곳만 채우면 그 환경만 동작.
- "앱은 뜨는데 일부 엔드포인트만 죽는다" → 거의 항상 **특정 의존성(여기선 DB 설정)** 문제.
- 필수 설정 누락을 **부팅 시점에 크래시**시키는 것도 한 방법(빨리 드러남) vs 지금처럼 요청 시점에 터지는 구조의 트레이드오프를 인지.
