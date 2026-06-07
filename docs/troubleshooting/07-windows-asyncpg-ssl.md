# 07. 로컬 통합 테스트만 실패 — 한글 사용자명 경로 + asyncpg SSL

## 증상
- 단위 테스트는 다 통과하는데 **통합 테스트 1건**(`test_api_integration`)만 로컬에서 에러.
- 에러: `OSError: [Errno 42] Illegal byte sequence` — `asyncpg/connect_utils.py`의 `ssl.load_cert_chain(...)`에서 발생.
- CI(Ubuntu)에서는 통과.

## 원인
- Windows 사용자명이 **비ASCII(한글: `김호준`)** → 홈 경로 `C:\Users\김호준\...`.
- asyncpg가 libpq 기본 동작으로 `~/.postgresql/postgresql.crt`를 로드하려다, **비ASCII 경로**를 처리하며 바이트 시퀀스 에러.
- 즉 **DB/코드 문제가 아니라 로컬 OS 환경 문제.** CI 리눅스는 ASCII 경로라 무사.

## 진단
- 단위는 OK, 통합만 실패 + 트레이스백이 우리 코드가 아니라 `asyncpg` 내부 SSL 로드 → 환경 의심.
- 에러 지점이 인증서 **파일 경로 로드**임을 확인 → 사용자명(한글) 연관.

## 해결
- 앱 런타임은 `config.get_ssl_context()`에서 **명시적 SSL 컨텍스트**를 만들어 asyncpg에 전달(libpq 기본 인증서 탐색을 우회). Supabase 풀러용으로 `check_hostname=False`, `verify_mode=CERT_NONE`(URL 자체가 비밀이라 MITM 표면 제한적).
- 로컬 통합 테스트는 testcontainers가 raw asyncpg 기본 경로를 타서 이 환경에선 실패 → **CI에서 검증**하는 것으로 수용(로컬에선 알려진 스킵 취급).

## 교훈
- **"로컬만 실패 / CI는 통과"는 OS 환경 차이**를 먼저 의심(경로·인코딩·권한).
- 비ASCII 사용자명/경로는 네이티브 라이브러리(libpq 등)에서 종종 터진다 → 라이브러리의 **암묵적 파일 탐색**을 명시적 설정으로 대체하면 환경 의존을 줄일 수 있다.
- 트레이스백이 **내 코드가 아니라 서드파티 내부**에서 끝나면 환경/설정 쪽을 본다.
