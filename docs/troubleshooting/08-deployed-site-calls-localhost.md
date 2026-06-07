# 08. 배포 사이트가 `localhost:8000`을 호출 — Vercel 빌드타임 env 누락

## 증상
- 배포 사이트에서 목록 로딩 실패. (02 CORS와 **증상이 똑같이** "불러오지 못함")
- F12 콘솔:
  ```
  Failed to load resource: net::ERR_CONNECTION_REFUSED
  localhost:8000/api/v1/players
  ```
- 즉 배포된 프론트가 **사용자 본인 PC(`localhost:8000`)** 를 부르고 있었다 → 당연히 거부.

## 원인
프론트 `lib/api.ts`:
```ts
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000"
```
- **Vercel에 `NEXT_PUBLIC_API_BASE_URL`이 설정되지 않아** 기본값 `localhost:8000`이 번들에 박힘.
- `.env.example`엔 안내가 있었지만, **대시보드에 실제 값을 안 넣은** 것이 함정.

## 진단
1. 콘솔이 가리키는 호출 대상이 `localhost:8000` → "환경변수 미주입"을 바로 시사.
2. 배포된 **JS 번들을 직접 grep**해서 어떤 URL이 박혔는지 확인:
   ```
   curl -s <site>/_next/static/chunks/<chunk>.js | grep -oE "https?://[^\"']*(code\.run|localhost:8000)[^\"']*"
   ```
   재배포 전: `localhost:8000`, 재배포 후: `...code.run` 으로 바뀐 것을 확인.

> 핵심: `NEXT_PUBLIC_*`는 **빌드 시점에 코드에 박힌다(baked-in)**. 런타임에 안 읽음.

## 해결
1. Vercel → Settings → Environment Variables → `NEXT_PUBLIC_API_BASE_URL = https://<northflank>.code.run` (끝 슬래시 없이, Production).
2. ⚠️ **반드시 재배포** (env 저장만으론 기존 번들이 안 바뀜). Deployments → Redeploy.
3. 브라우저 **하드 리프레시 / 시크릿 창** (옛 번들 캐시 제거).

## 교훈
- **`NEXT_PUBLIC_*` = 빌드타임.** 값 추가 후 **재배포**가 필수. "저장했는데 안 됨"의 단골 원인.
- 02(CORS)와 **증상이 동일**("배포만 로딩 실패")하지만 원인이 다르다 → **콘솔의 실제 호출 URL**을 보면 즉시 갈린다: `localhost:8000`이면 env 누락, `code.run`인데 막히면 CORS.
- "고쳤는데 안 보임"의 절반은 **브라우저 캐시**. 시크릿 창으로 서버 상태와 캐시 문제를 분리해서 본다.
