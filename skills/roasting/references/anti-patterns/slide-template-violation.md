---
name: SLIDE_TEMPLATE_VIOLATION
description: HTML 슬라이드 산출물에서 진짜 베이스 룰 위반. <deck-stage>·deck-stage.js 같은 환각 룰 사용, 1920px 고정 폭, .deck 컨테이너 누락, cqi 단위 누락 등 사용자 화면에서 깨지는 사고 차단 (v0.4.8 신설)
applies_to_categories:
  - 의사결정·전략  # c41 임원 PPT, c45 컨설팅 덱
  - 외부 커뮤니케이션  # c42 강의 자료
  - 마케팅  # c70 랜딩, c73 웹사이트, c74 이미지(슬라이드형)
  - generic_case (HTML 슬라이드 모드)
severity: critical
---

# SLIDE_TEMPLATE_VIOLATION — 슬라이드 베이스 룰 위반

## 배경

v0.4.6~v0.4.7 동안 BLACK이 HTML 슬라이드를 작성할 때 다음 환각 룰을 따랐다:
- `<deck-stage>` 커스텀 엘리먼트
- `deck-stage.js` 스크립트 로드
- `width: 1920px; height: 1080px` 고정 픽셀

문제는 셋 다 가공이었다. `deck-stage.js`는 GitHub Pages에서 **404** (존재하지 않음), `<deck-stage>`는 어떤 슬라이드 템플릿에도 안 쓰임, 1920×1080 고정은 사용자 노트북에서 화면을 넘쳐 깨졌다. v0.4.7 후쿠오카 케이스가 그 사고. RGSB BLUE 페르소나도 "코드 구조만" 확인하고 실제 렌더링은 못 검증해 9.6 통과시켰다.

진짜 슬라이드 템플릿(airoasting.github.io/slide_library/templates/*)은:
- JavaScript 0줄
- `<div class="deck">` + `<div class="slide">` 구조
- `max-width: 1200px` 컨테이너
- `aspect-ratio: 16 / 10` (16:10 비율 자동)
- `container-type: inline-size` (CSS 컨테이너 쿼리)
- `cqi` 단위 (5cqi, 1.05cqi, clamp(8px, 1.05cqi, 16px))

이 룰은 모든 HTML 슬라이드 산출물에 적용. 환각 룰 차단 + 진짜 룰 강제.

## 검출 기준

다음 중 **하나라도** 양성이면 즉시 BLACK 재작성:

### A. 환각 룰 사용 (절대 금지)
1. `<deck-stage>` 또는 `</deck-stage>` 태그 사용 (0회여야 함)
2. `deck-stage.js` 문자열 사용 (스크립트 로드 0회)
3. `width: 1920px` 또는 `height: 1080px` 고정 픽셀

### B. 진짜 베이스 룰 누락
4. `<div class="deck">` 또는 동등 컨테이너 구조 1회 누락
5. `aspect-ratio: 16 / 10` (또는 `16/10`) CSS 누락
6. `container-type: inline-size` CSS 누락
7. `cqi` 단위 사용량 10회 미만 (실제 정상 작성은 50회 이상)

### C. JS 의존 (슬라이드 케이스에서 금지)
8. 슬라이드 케이스 (`html_mode: slides|assisted`)에서 `<script` 태그 사용 (인터랙티브 보강조차 무-JS로 가능: `<details>`·`:target`·CSS 트랜지션)

## 검출하지 않는 것

- `direct` 모드 (c73 웹사이트 제작) — 풀스택 페이지라 컨테이너 쿼리·1200px 룰 강제 안 함. 별도 룰 적용.
- 1920×1080 픽셀이 폰트 file URL 같은 곳에 우연히 들어간 경우 (실제 사이즈 지정이 아니면 무시)
- `<script>` 가 폰트 load·analytics·viewport meta 같은 비-인터랙티브 용도일 때 (드물지만 가능)

## 양성 예시 5

1. **HTML 슬라이드에 `<deck-stage>` + `deck-stage.js` 사용** (v0.4.7 후쿠오카 사고)
   ```html
   <script src="https://airoasting.github.io/slide_library/templates/tri-color-magazine/deck-stage.js"></script>
   <deck-stage>
     <section class="s-cover">...</section>
   </deck-stage>
   ```
   → 404 스크립트 + 가공 엘리먼트로 화면 깨짐.

2. **1920×1080 고정 픽셀 사용**
   ```css
   .slide { width: 1920px; height: 1080px; }
   ```
   → 사용자 노트북 1440px·1366px 화면에서 가로 스크롤·잘림.

3. **`.deck` 컨테이너 누락**
   ```html
   <body>
     <section class="slide">...</section>
     <section class="slide">...</section>
   </body>
   ```
   → max-width 1200 적용 안 됨, 전체 폭 노출.

4. **aspect-ratio 누락, height 고정**
   ```css
   .slide { width: 100%; height: 800px; }
   ```
   → 컨테이너 폭 변화 시 비율 깨짐.

5. **cqi 단위 누락, 모든 폰트·여백을 px로**
   ```css
   .slide-title { font-size: 48px; padding: 40px; }
   ```
   → 컨테이너 크기 변해도 폰트 그대로 → 좁은 화면에서 텍스트 잘림.

## 음성 예시 5

1. **진짜 베이스 룰 준수** (v0.4.8 후쿠오카 R2 / 4050 액션 R2)
   ```html
   <body>
     <div class="deck">
       <div class="slide dark">...</div>
       <div class="slide">...</div>
     </div>
   </body>
   ```
   + CSS에 `aspect-ratio: 16 / 10` + `container-type: inline-size` + `font-size: clamp(8px, 1.05cqi, 16px)` ✓

2. **콘텐츠 폰트가 모두 cqi 단위**
   ```css
   .action-title { font-size: 2.4cqi; }
   .columns { gap: 3cqi; padding: 5cqi; }
   ```
   ✓ 컨테이너 폭 변화에 자동 스케일.

3. **`direct` 모드(c73)에서 1920px 사용은 OK**
   - direct 모드는 슬라이드 데크가 아니라 풀스택 웹사이트이므로 이 룰 적용 안 함.

4. **인터랙티브 보강을 무-JS로**
   ```html
   <details><summary>액션 3 보기</summary><p>...</p></details>
   ```
   ✓ JS 0줄 룰 유지.

5. **폰트 link만 `<head>`에 있고 본문 JS 없음**
   ```html
   <head>
     <link href="https://fonts.googleapis.com/..." rel="stylesheet">
   </head>
   ```
   ✓ 폰트 로드는 `<link>` 태그, `<script>` 아님.

## BLACK 재작성 지시 템플릿

```
직전 산출물에 SLIDE_TEMPLATE_VIOLATION 안티패턴이 검출되었습니다:

검출된 위치:
- {위반 항목: <deck-stage> 사용 / 1920px 고정 / aspect-ratio 누락 등}

재작성 지시:
1. 환각 룰 (<deck-stage>·deck-stage.js·1920px) 완전 제거.
2. 진짜 베이스 룰 적용:
   - <div class="deck"> 컨테이너 + <div class="slide"> N개
   - max-width: 1200px 컨테이너
   - aspect-ratio: 16 / 10
   - container-type: inline-size
   - 모든 폰트·여백을 cqi 단위로 (font-size: clamp(8px, 1.05cqi, 16px))
3. 슬라이드 케이스면 <script> 0회 (JS 의존 금지).
4. 베이스 구조 상세는 agents/roasting-black.md "HTML 산출물 베이스 룰" v0.4.8 절 참조.
5. 라운드 카운트는 변동 없습니다.
```

## 적용 제외

- `html_mode: direct` (c73 웹사이트 제작) — 풀스택 페이지, 별도 룰.
- Markdown 산출물 — HTML 베이스 룰 자체 무관.
- 슬라이드 템플릿 자체 (sliders_library 원본 HTML) — 본 룰의 검증 대상이 아니라 베이스.
