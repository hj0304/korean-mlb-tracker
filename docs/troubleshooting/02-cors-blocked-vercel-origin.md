# 02. 배포 사이트에서만 "선수 목록을 불러오지 못했습니다" — CORS 차단

## 증상
- 로컬(`npm run dev`)에서는 목록이 잘 뜸.
- **배포된 Vercel 사이트**에서는 헤더 타이틀은 보이는데 목록 자리에 에러 UI("불러오지 못했습니다 / 다시 시도").
- 즉 **새 프론트는 배포됐고**(타이틀이 새 버전), 데이터만 못 가져옴.

## 원인
백엔드 `CORS_ALLOW_ORIGINS`에 **Vercel 프로덕션 주소가 없었다.**
- 타이틀은 서버에서 렌더되니 보임.
- 목록은 **브라우저가** 백엔드를 호출 → 백엔드가 그 origin을 CORS 허용하지 않아 브라우저가 응답을 차단 → fetch 실패 → 에러 UI.
- 로컬은 `http://localhost:3000`이 기본 허용이라 OK. → **로컬 OK / 배포 NG**.

## 진단
1. 백엔드 직접 호출(curl) → `/api/v1/players` **200**. 즉 백엔드·DB는 정상.
2. 그런데 브라우저만 실패 → CORS 의심.
3. `curl`에 **실제 origin 헤더**를 붙여 응답 헤더 확인:
   ```
   curl -s -D - -o /dev/null -H "Origin: https://<vercel-app>" <API>/api/v1/players \
     | grep -i access-control-allow-origin
   ```
   → 헤더 **없음** = 그 origin은 허용 목록에 없음(차단).

> 핵심: `curl`은 CORS를 강제하지 않아 200으로 보인다. **CORS는 브라우저만 막는다.** 그래서 "curl은 되는데 브라우저는 안 됨"이면 CORS를 의심.

## 해결
Northflank → Environment variables → `CORS_ALLOW_ORIGINS`에 정확한 프로덕션 origin 추가(콤마 구분):
```
http://localhost:3000,https://korean-mlb-tracker-sabior-s-projects.vercel.app
```
→ 재시작. 이후 응답에 `access-control-allow-origin` 헤더가 정상 출력됨.
브라우저 쪽은 **하드 리프레시(Ctrl+Shift+R)**로 캐시 비우면 반영.

## 교훈
- CORS origin은 **글자 하나까지 정확 일치**(scheme 포함, 끝 슬래시 없음).
- Vercel **프리뷰 URL은 배포마다 바뀐다** → 매번 env에 넣기 번거로우면 `allow_origin_regex`로 프로젝트 패턴을 허용하는 방법도 있음(프로덕션만 쓰면 고정 URL 하나로 충분).
- "로컬 OK / 배포 NG" 디버깅 3대장: **env 누락 · 리전 · CORS**.
