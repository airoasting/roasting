---
name: FAKE_IMAGE_URL
description: HTML/Markdown 산출물의 이미지 URL이 검증되지 않거나 환각된 패턴. 가짜 외부 URL을 만들어 넣으면 브라우저에서 broken image로 표시되거나 잘못된 콘텐츠가 노출됨 (v0.4.5 신설)
applies_to_categories:
  - 마케팅
  - 의사결정·전략 (HTML 케이스)
  - generic_case (HTML/assisted 모드)
severity: high
---

# FAKE_IMAGE_URL — 가짜·미검증 이미지 URL

## 검출 기준

다음 중 하나라도 BLACK 산출물에 나타나면 양성:

1. **추측성 URL:** `https://example.com/images/seoul.jpg`, `https://images.unsplash.com/photo-123456`처럼 BLACK이 임의로 만든 것 같은 URL.
2. **fetch 불가 URL:** `WebFetch`로 200 응답을 확인하지 않은 외부 이미지 URL이 `<img src=...>`에 들어 있다.
3. **CDN 추정 URL:** `https://cdn.{브랜드}.com/...` 같은 추정 패턴.
4. **placeholder 미사용:** 출처를 찾지 못했는데 어떤 URL이든 src로 박아놓은 경우.

## 검출하지 않는 것

- 사용자가 입력에서 직접 제공한 URL
- WebFetch로 200 응답이 확인된 공식 페이지 이미지
- `<div class="img-placeholder">` 같은 명시적 자리표시자 (이게 권장 패턴)
- data URI (`data:image/...`)나 inline SVG

## 양성 예시 5

1. `<img src="https://www.npm.gov.tw/images/jadeite-cabbage.jpg" alt="취옥백채">` → 추측 URL, fetch 미확인
2. `<img src="https://cdn.taipei101.com.tw/hero.jpg">` → 추정 CDN 패턴
3. `![취옥백채](https://example.com/img/jade.jpg)` → 명백한 더미 URL
4. `<img src="https://images.unsplash.com/photo-1234567890-abcde">` → Unsplash 형식이지만 photo-ID가 검증 안 됨
5. `<img src="/assets/hero.jpg">` → 상대 경로지만 실제 파일 없음 (HTML 단일 파일 산출물에서)

## 음성 예시 5

1. `<div class="img-placeholder" role="img" aria-label="국립고궁박물원 외관 — 공식 이미지로 교체 권장">[이미지 자리: 박물원 외관]</div>` → 명시적 자리표시자 ✓
2. 사용자가 입력에 첨부한 URL을 그대로 src로 사용 ✓
3. `WebFetch`로 200 OK 확인한 박물원 공식 페이지의 이미지 URL ✓
4. `[이미지 권장: 5월 타이베이 야경]` (Markdown 자리표시자) ✓
5. inline SVG로 직접 그린 아이콘 ✓

## BLACK 재작성 지시 템플릿

```
직전 산출물에 FAKE_IMAGE_URL 안티패턴이 검출되었습니다:

검출된 URL:
- {fake_url}

재작성 지시:
1. 이 이미지에 대해 사용자가 제공한 URL이 있는지 입력을 재확인하세요.
2. 없다면 WebFetch로 공식 출처(박물원·기관·회사) 페이지에서 실제 이미지 URL을 찾으세요.
3. 그래도 안 되면 무료 라이선스 스톡(Unsplash 검색) 또는 명시적 자리표시자(<div class="img-placeholder">)로 교체하세요.
4. 가짜 URL을 만들어 채우지 마세요. 라운드 카운트는 변동 없습니다.
```

## CSS 권장 자리표시자 스타일

`<div class="img-placeholder">` 사용 시 다음 CSS를 함께 인라인 주입:

```css
.img-placeholder {
  width: 100%;
  aspect-ratio: 16 / 9;
  background: #EEE;
  border: 1px dashed #999;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #666;
  font-size: 13px;
  text-align: center;
  padding: 16px;
  margin: 16px 0;
}
```

## 적용 제외

- Markdown 산출물에서 `[이미지 권장: ...]` 한 줄 표기는 검사 면제 (자리표시자 명시)
- 이메일·공지·내부 메모 등 이미지가 본래 없는 카테고리
