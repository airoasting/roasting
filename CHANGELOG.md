# Changelog

This project follows [Semantic Versioning](https://semver.org/) and [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

## [0.4.12] - 2026-05-17

### Changed (Korean Jargon Block — Strong-Verb Trap)

- **회의실 jargon 사전 대폭 확장 (3카테고리 분류).** v0.4.10에서 "박다·즉시·가동·확장"만 잡았던 미흡 보완:
  - **(A) 강한 단음절 동사 + 의지 종결:** `박다·갈다·꽂다·민다·말다·돌리다·태우다·털어내다·깎다·굴리다·치고 들어가다` + `~야 한다` 패턴 모두 차단. 영어 imperative 동사(drive·hammer·push·grind·pound) 무의식적 번역체.
  - **(B) 영어 번역체 부사·명사:** `즉시 실행·즉시 가동·동시에 가동·분기 리듬으로 가동` (v0.4.10 유지).
  - **(C) 시스템 명사화 jargon (신설):** `재편·재구성·흡수·압축` (사람·직무·인원 맥락에서 자연어 아님), `구축·구성·운영체계` 명사구, `~확장·~강화·~제고` 명사구.
- **메타 원칙 신설 — "Strong-Verb Translation Trap".** 강한 단음절 동사 + "~야 한다" 패턴은 영어 imperative 번역체일 가능성이 매우 높음. 한국 시니어 임원·일반 독자는 안 씀. "단호한 컨설팅 톤"은 *결론의 명료함*에서 나오지 *어휘의 강도*에서 나오지 않는다.
- **`references/korean-polish.md` 부록 사전 3카테고리로 재구조화.** 항목 수 13 → 30+로 확장. 메타 원칙 절 신설.
- **`agents/roasting-black.md` Self-Check BLUE 축 확장.** v0.4.10 한 줄 → 3카테고리 + 메타 원칙으로 세분.
- **`agents/roasting-blue.md` 평가축 강화.** 강한 단음절 동사 검출 시 점수와 별개로 "메타 원칙 위반: 영어 imperative 번역체 의심" 한 줄 코멘트 의무화.

### Rationale

2026-05-17 호출(`20260517_06`, c45) v0.4.10 패치 적용 후, 사용자가 "평판·결정·연결을 동시에 갈아야 합니다"에서 "갈아야 한다"가 한국어가 아니라고 추가 지적. 검증 결과 v0.4.10 사전이 "박다"만 잡고 동족 어휘("갈·꽂·민·말·돌리·태우·털·깎·굴리")를 망라하지 못한 시스템 한계 확인. 더 근본적으로 BLACK이 "단호한 톤" 표현 시 영어 imperative 동사를 강한 단음절 동사로 자동 번역하는 학습 편향이 있어 메타 원칙 명문화 필요.

### Impact

기존 호출 호환성 영향 없음. 다음 /roasting 호출부터 30+개 jargon 어휘 검출 + 메타 원칙 코멘트 자동 활성화. R1 평균 한국어 자연스러움 추가 +0.3~0.5점 개선 예상.

## [0.4.11] - 2026-05-17

### Changed (Case ID Prefix Rename)

- **케이스 ID 접두사 일괄 변경:** 이전 접두사 → `c` (총 68개 케이스, ID는 `c1`~`c76`). 기존 접두사가 prompt·page 등 의미와 충돌해 `c`(case)로 통일.
- **변경 범위:**
  - `references/cases/` 폴더의 케이스 파일 68개 이름 변경 → `c1.md` ~ `c76.md`
  - 각 케이스 파일 frontmatter `id` 필드 접두사 변경
  - `references/cases/_index.md` 68회 라우팅 참조 갱신
  - `SKILL.md` 28회 본문 참조 갱신 (Ecosystem enrich 표·사용 예시·참조 인덱스 등)
  - `agents/roasting-black.md` 14회 (HTML 산출물 케이스 표 등)
  - `references/output-formats.md` 13회
  - `references/anti-patterns/slide-template-violation.md` 6회 + `internal-contradiction.md` 2회
  - `tests/routing/cases_phrasings.json` 204회 + `cases_phrasings.seed.json` 189회 + `tests/quality/scenarios.json` 18회 + 기타 테스트 파일
  - 본 CHANGELOG 이전 노트 21회 (역사 일관성)
  - 총 참조 약 600+회 자동 치환
- **백업:** 작업 전 `roasting.bak.20260517-{HHMMSS}/` 폴더로 전체 백업.

### Rationale

`p`는 prompt·page 등 여러 의미와 충돌. `c`는 case 의미가 명확. 케이스 라이브러리 호출·라우팅·로깅에서 ID 가독성 +. 사용자 2026-05-17 직접 요청.

### Migration Note

기존 사용자 작업 history(`~/Desktop/Roasting/{YYYYMMDD}_{NN}/`)의 `routing.json`·`reasoning.md`·`critique.md`는 그대로 둠 (역사 기록 보존). 새 호출부터 자동으로 `c*` 사용. 이전 ID로 저장된 옛 호출 history 참조 시 ID 접두사만 `c`로 바꿔 1:1 매핑하면 됨 (숫자 부분은 동일).

## [0.4.10] - 2026-05-17

### Added (Korean Jargon Block)

- **11번째 한국어 패턴 신설 — "회의실 jargon 어휘".** Phase 6.5 한국어 검증 10패턴 → 11패턴으로 확장. 차단 어휘: `박다·박습니다·박아야`(시간/계획 맥락), `즉시 실행·즉시 가동`, `동시에 가동·분기 리듬으로 가동`, `~확장·~강화·~제고` 명사구 결합, `올린다·돌린다·태운다·털어낸다`(jargon 의미). 컨설팅·스타트업 회의실에서는 통하지만 시니어 임원·일반 독자에게는 어색해 사람 글로 안 읽히는 근본 사각지대 차단.
- **`references/korean-polish.md` 부록 "jargon → 자연 표현 사전" 신설.** 13개 jargon 표현의 자연 한국어 대체 표현 사전. BLACK 재작성·R3 패치에서 즉시 참조 가능.
- **`agents/roasting-black.md` Self-Check BLUE 축에 1줄 추가.** BLACK 1차 작성 후 jargon 어휘 0회 자체 검증 의무화.
- **`agents/roasting-blue.md` 평가축 신설.** RGSB BLUE가 헤드라인·본문에서 jargon 검출 시 -0.5점/회 적용. 5회 이상은 평균 -1.0점 추가.

### Rationale

2026-05-17 호출(`20260517_06`, c45 컨설팅 덱)에서 사용자가 "박다·즉시 실행" 표현이 자연스러운 한국어가 아니라고 직접 지적. 검증 결과 4개 게이트 모두(BLACK Self-Check BLUE 축 / RGSB BLUE / Phase 6.5 10패턴 grep / 6항 자체검증) 어휘 자연스러움을 안 보는 구조적 사각지대 확인. 한국어 등급 A(9.5)가 사람 귀로는 어색한 결과를 통과시키던 문제 해소.

### Impact

기존 호출 호환성 영향 없음. 다음 /roasting 호출부터 jargon 검출이 자동 활성화. 임원·일반 독자 대상 산출물의 한국어 자연스러움 +0.5~1.0점 개선 예상.

## [0.4.9] - 2026-05-17

### Changed (Docs Slim Pass)

- **SKILL.md 본문에서 v0.4.2/0.4.3/0.4.4/0.4.5/0.4.6/0.4.7/0.4.8 등 인라인 버전 주석 30+곳 일괄 제거.** 본문이 "현재 동작 가이드"로만 읽히도록 정리. 룰 정당화·회고 문구는 보존 (BLACK이 룰의 *이유*를 학습하는 데 필요). 시간 마커("v0.X.X 신설"·"v0.X.X부터"·"v0.X.X 통일")만 추출. 핵심 뼈대(5 원칙·7-Phase·9 안티패턴·Trust 룰·Korean Polish Pass·4종 산출물·표준 푸터·Ecosystem·Design Taste Integration) 무손실.
- **References 표·푸터의 버전 라벨 정리:** `(v0.4.8 신설)`·`(v0.4.8부터)`·`v0.4.8` 등 시점 라벨 제거. CHANGELOG.md 단일 진실 원천화.
- **`### 검증된 품질 지표` 헤더에서 "v0.2 측정값, v0.3·v0.4에서 회귀 없음" → "베타 측정값, 후속 패치에서 회귀 없음"으로 일반화.** 버전 시점에 묶이지 않는 표현으로 변경.
- **GA 표기 일반화:** "v1.0 GA에 활성화" → "GA에 활성화 예정" 등 현재 베타 시점 의존 문구 제거.

### Rationale

skill-creator 루브릭 적용 시 SKILL.md 본문 토큰 비용이 매 호출마다 부과되는데, 인라인 버전 주석은 (a) 현재 시점에서는 "이게 언제 도입됐는지" 정보가 BLACK·RGSB의 산출에 영향을 주지 않고 (b) CHANGELOG.md가 이미 같은 정보를 시계열로 보유하므로 중복이다. 본문은 "현재 룰이 무엇이고 왜 그래야 하는가"에 집중, 시간 정보는 CHANGELOG로 단일화한다.

### Migration Note

기능 변경 0. 동작 변경 0. 의미상의 변경 0. 본문 일부 줄에서 회고 시제만 "v0.4.X부터 ~한다" → "~한다"로 바뀐 정도. 기존 호출·산출물 호환성 무영향.

## [0.4.8] - 2026-05-17

### Removed (Hallucinated Rule Purge)

- **v0.4.6/v0.4.7 "`<deck-stage>` + `deck-stage.js` 강제" 룰 폐기.** 두 항목 모두 환각이었다 — `deck-stage.js`는 GitHub Pages 404 (실재하지 않는 파일), `<deck-stage>`는 어떤 슬라이드 템플릿에도 안 쓰이는 가공 엘리먼트. v0.4.7 후쿠오카 검증 런이 사용자 화면에서 깨진 근본 원인. SKILL.md Phase 2 베이스 룰 + agents/roasting-black.md "HTML 산출물 베이스 룰" 절 전면 개정.

### Added

- **9번째 안티패턴 `slide-template-violation` 신설** (severity: **critical**). HTML 슬라이드 산출물에서 진짜 베이스 룰 위반 검출. 환각 룰 사용 (`<deck-stage>`·`deck-stage.js`·1920×1080 고정), 진짜 룰 누락 (`.deck`·`aspect-ratio: 16/10`·`container-type: inline-size`·`cqi` 단위), 슬라이드 케이스에서 `<script>` 사용을 모두 잡는다. 양성/음성 예시 5개씩.
- **agents/roasting-black.md "HTML 산출물 베이스 룰" v0.4.8 전면 개정** — 진짜 슬라이드 베이스 구조(`<div class="deck">` + `<div class="slide">` + `max-width: 1200px` + `aspect-ratio: 16/10` + `container-type: inline-size` + `cqi` 단위 + JS 0줄) 명시 + 8개 grep 검증 체크리스트.
- **BLACK Self-Check에 BLUE 축 1항 추가** — HTML 슬라이드 케이스에서 진짜 베이스 룰 준수 자체 검증.
- **"Honest Reporting Rule" 신설** (agents/roasting-black.md) — v0.4.7 회고에서 Self-Check 거짓 통과 사례 다수 누적. 메인 Claude가 grep으로 교차 검증한다는 사실을 BLACK에게 명시, 거짓 통과 보고 금지.
- **Phase 4 강화 — BLACK Self-Check + 메인 grep 교차 검증 의무화** (SKILL.md). 메인 Claude가 BLACK 산출물 받은 직후 환각 룰 0회·em dash 0회·진짜 베이스 룰 존재 등 8개 grep 패턴 실행.

### Fixed

- **v0.4.7 검증 런 사고 1건** (실측 회귀):
  1. 사용자가 후쿠오카 케이스 출력을 열었을 때 "다 깨졌는데?" 보고 → 진짜 mckinsey-navy 템플릿이 JS 0줄 + CSS 컨테이너 쿼리 구조라는 사실 확인 → 환각 룰 폐기 + R2 재작성 (`.deck` + `aspect-ratio: 16/10` + `cqi` 단위) → 화면 정상 렌더링 확인.

### Added (Korean Polish Pass)

- **Phase 6.5 한국어 검증 의무 패스 신설.** Phase 6 게이트 통과 직후, Phase 7 출력 직전에 산출물의 한국어가 사람 글로 읽히는지 검증한다. /roasting의 RGSB는 콘텐츠 품질을, 본 패스는 한국어 자연스러움을 본다 (독립 레이어).
- **두 가지 실행 모드:**
  - **간소 모드 (기본, 자동):** 메인 Claude가 10패턴 grep + 6항 자체검증 + AI 티 점수 산출. 1~2분 추가.
  - **정밀 모드 (옵션):** BLACK polish 페르소나 + RGSB 4인 풀 패스. 사용자 명시 요청 또는 간소 모드 등급 C·D 컨펌 시 진입.
- **AI 티 10패턴 정량 룰:** 번역투·영어 인용·기계적 병렬·관용구·피동태·접속사·리듬·이모지·추측·메타. 심각도 L3(결정적, 1개라도 fail)·L2(강함, 3개 이상 fail)·L1(약함).
- **AI 티 점수 + 등급:** 점수 = 10 − (L3 × 2.0) − (L2 × 0.5) − (L1 × 0.2). 등급 A(점수 ≥ 9.0 + L3 = 0)·B(8.0~8.9 + L3 = 0 + L2 ≤ 4)·C(L3 1~2 또는 7.0~7.9)·D(L3 ≥ 3 또는 < 7.0).
- **6항 자체검증:** 의미 동등·변경률·말투 일관·장르 이탈 없음·AI 티 등급 A 또는 B·em dash 0개.
- **산출물 자동 수정 금지.** 본 패스가 자동으로 BLACK을 재호출해 산출물을 수정하지 않는다. 등급 A·B 통과, C·D면 사용자 컨펌 후 처리.
- **새 산출물 1종 추가** (`final/korean-polish.md`) — 등급·AI 티 점수·10패턴 카운트·6항 자체검증 결과. 산출물 총 3종 → **4종**으로 확장.
- **references/korean-polish.md 신설** — 사용자 제공 5인 페르소나 시스템 프롬프트 원문 보존 + /roasting 통합 절차.

### Migration Note

기존 v0.4.6/v0.4.7로 생성된 HTML 슬라이드 산출물(오사카 일정·후쿠오카 일정·이전 4050 액션 R1)은 모두 환각 룰을 따랐기 때문에 사용자 화면에서 깨질 가능성이 있다. 필요 시 BLACK 재호출로 v0.4.8 베이스 룰 재적용 권고. 본 패치와 함께 4050 액션 케이스(20260517_04)의 final/output.html은 R2(진짜 베이스 룰)로 이미 교체 완료. Phase 6.5 한국어 검증 패스는 v0.4.8 이후 새 호출부터 자동 적용.

## [0.4.7] - 2026-05-17

### Added

- **입력 사전 처리 (SKILL.md Phase 2-3 신설 — Pre-Processing Pack)** — BLACK 호출 전에 메인 Claude가 사용자 입력의 빈칸·날짜·1차 출처를 미리 처리해 패키지로 박아준다. 3개 영역:
  1. **날짜·시간 정합성** — 상대 날짜(다음주 금요일·이번 주말 등)를 오늘 기준 절대 날짜·요일로 환산해 `dates_resolved`로 저장.
  2. **누락 파라미터 기본값 + 명시 라벨** — 인원·예산·출발지·동반자 같은 결정 핵심 파라미터에 합리적 기본값 박고 산출물 표지에 명시 라벨로 노출.
  3. **1차 출처 화이트리스트** — fact-heavy 입력에 도메인별 1차 출처(항공사 공식·DART·외교부·기상청 등) 화이트리스트를 BLACK에 박아 2차 출처(블로그·KKday)만 보고 작성하는 패턴 차단.
  - 결과를 `{session_dir}/pre-processing.json`에 저장하고 BLACK 프롬프트 머리에 첨부.
- **BLACK 자기 점검 체크리스트 (agents/roasting-black.md "Self-Check Before Submit" 절 신설)** — 1차 작성 직후 RGSB 4인의 채점 기준을 BLACK이 스스로 미리 돌린다. RED(이성·구조·근거 5항), SILVER(도메인 디테일·관행 4항), BLUE(호흡·가독성 5항), GOLD(실사용 시나리오 4항). 미통과 항목은 그 자리에서 자체 수정(라운드 카운트 안 깎임). R1 평균 8.7→9.2 목표.
- **8번째 안티패턴 `internal-contradiction` 신설** — BLACK 산출물 내부의 자기 모순 검출. 라벨↔본문 충돌, 동일 객체 수치 불일치, Pre-Processing Pack과 본문 충돌, 헤더↔본문 약속 불일치, 날짜·요일 자가 모순 5종 패턴. 양성/음성 예시 5개씩 + 재작성 지시 + 적용 제외 (소설·시·심리상담). 모든 일반 카테고리에 적용.
- **RGSB 코멘트 Trust 룰 (SKILL.md Phase 6.1 신설)** — BLACK이 RGSB 코멘트를 받았을 때 명백한 사실 오류 코멘트(Pre-Processing Pack 충돌·1차 출처 충돌·페르소나 정의 충돌)는 `round-{n}/rejected-comments.md`에 사유 명시 후 기각 가능. 나머지 도메인 디테일·시나리오 빈칸·매거진 톤 코멘트는 반영 의무. 한 라운드에 같은 페르소나 코멘트 2건 이상 기각 시 사용자 알림(캐스팅 재검토).

### Changed

- **Phase 4 검출 룰 7종 → 8종** — `internal-contradiction` 추가로 룰 개수 갱신. 참조 파일 인덱스 동기화.
- **Phase 3 BLACK 입력 프로토콜** — `Pre-Processing Pack`을 명시적 입력 항목으로 추가. 기존 케이스 정의·슬라이드 템플릿·이전 라운드 코멘트·enrichments에 더해진다.
- **enrich 절 번호 재정렬** — 기존 2-3 Enrich Field가 2-3 입력 사전 처리 신설로 인해 2-4로 이동. SKILL.md 본문의 "Phase 2-3" 참조를 "Phase 2-4"로 동기화.

### Fixed

- **v0.4.6 오사카 여행 일정 사고 4건 일괄 차단** (실측 회귀):
  1. RED가 5/22 요일을 토요일로 오판정 → Pre-Processing Pack `dates_resolved`로 사전 환산 + Trust 룰로 BLACK이 기각 가능.
  2. 인터컨티넨탈 area 라벨 "신사이바시" vs desc "우메다 그랜드 프론트 직결" 자기 모순 → `internal-contradiction` 안티패턴 신설로 Phase 4에서 검출.
  3. 라피트 1,490엔이 2차 출처 KKday 기준이라 웹 할인가 누락 → 1차 출처 화이트리스트로 난카이 공식 우선 시도 강제.
  4. GOLD가 R1에서 "1인/2인 분기 빈칸"으로 8.2 깎음 → Pre-Processing Pack `param_defaults`로 기본값 명시 라벨 강제.

## [0.4.6] - 2026-05-17

### Added

- **슬라이드 템플릿 선택 프로세스 강제 (SKILL.md Phase 2-2 신설)** — `slides`·`landing`·`assisted` 모드 모든 호출에서 35종 인덱스에서 **반드시 top-3 후보 추출 → 1순위 1개 선택**. 자동 패스 금지. 1순위 + 2·3순위 + 각 선택 사유를 `reasoning.md`의 "Slide Template Selection" 절에 강제 기록. 사용자에게는 1줄 알림(부담 0턴), 명시적 요청 시 2순위로 교체. v0.4.5까지 preferences 자동 적용으로 디자인 선정이 블랙박스가 되던 약점 해소.
- **HTML 산출물 베이스 룰 4종 (agents/roasting-black.md)** — 모든 HTML 모드 공통:
  1. **assisted 모드 슬라이드 템플릿 fetch 강제** — BLACK이 `WebFetch`로 베이스 HTML 받고 `<head>`/디자인 토큰 보존 후 컨테이너에 콘텐츠만 주입. "톤 차용·가이드라인 참고" 해석 금지. 자체 인라인 CSS 처음부터 작성 금지(=`direct` 영역 침범).
  2. **데스크톱 폭 베이스** — `.container { max-width: 1100px; padding: 48px 32px; }` + 텍스트 `max-width: 720px`. 모바일(`≤ 768px`) 반응형은 별도. 데스크톱에서 600~800px 좁은 페이지가 나오면 BLUE 안티패턴.
  3. **외부 폰트 로드 베이스** — Playfair Display·Noto Serif KR·Pretendard·Inter 등 비-시스템 폰트를 `font-family`에 쓰면 `<head>`에 Google Fonts/Pretendard CDN `<link>` 자동 주입 강제. v0.4.5까지 폰트 선언만 하고 로드 코드 누락으로 시스템 fallback으로 떨어지던 사고 차단.
  4. **이미지 URL HTTP 검증 강화** — Phase 4에서 메인 Claude가 `curl -sI -o /dev/null -w "%{http_code}"`로 모든 `<img src>` URL 200 응답 검증. 404/403/timeout이면 `FAKE_IMAGE_URL` 양성 → BLACK 재작성 또는 자리표시자 강제 교체.

### Changed

- **`fake-image-url` 안티패턴 강화** — 검출 기준에 "HTTP 검증 실패 URL"을 1순위 기준으로 추가. 도메인이 Unsplash·공식 사이트라도 ID/경로 환각으로 404가 나면 즉시 양성. Unsplash photo ID는 일정한 패턴이 없어 BLACK이 추측하면 거의 항상 404 — WebSearch + WebFetch로 unsplash.com 검색 페이지에서 실제 노출된 photo URL 추출만 허용.
- **BLACK 도구 활용 패턴** — assisted 모드에서 `WebFetch`로 슬라이드 템플릿 fetch가 필수 호출이 됨. 이전엔 fact-grounding용 선택적 호출이었음.

### Fixed

- **v0.4.5 타이베이 호출 사고 4건 일괄 차단** (실측 회귀):
  1. Unsplash photo ID 환각 → HTTP 404 (지금 룰: 사전 검증 + 사후 검증 이중)
  2. assisted 모드가 사실상 direct로 작동, 디자인 시스템 부재 (지금 룰: WebFetch 강제)
  3. 데스크톱 폭 680px로 좁음 (지금 룰: 1100px 컨테이너 베이스)
  4. Playfair Display·Noto Serif 선언만 하고 외부 폰트 로드 누락 (지금 룰: `<link>` 자동 주입)

## [0.4.5] - 2026-05-17

### Added

- **Fact-Grounding 규약 (출처 강제)** — BLACK이 fact-heavy 도메인(여행·식당·회사·통계·뉴스·인물·가격·사양) 신호 감지 시 WebSearch/WebFetch로 1차 출처를 확보한 뒤 인라인 링크·footnote로 산출물에 박는 새 행동 규약. 출처를 못 찾으면 그 사실 자체를 빼거나 "현장 확인 권장" 같은 안전 표현 사용. 환각으로 채우는 행위 금지.
- **이미지 규약 (출처 포함 시각 자료)** — HTML 산출물(slides·landing·direct·assisted)과 시각 친화 Markdown(여행·브랜드·회사 분석)은 BLACK이 적절한 시각 자료 포함. 우선순위: ① 사용자 제공 ② 공식 출처 ③ 무료 라이선스 스톡(Unsplash) ④ 명시적 자리표시자(`<div class="img-placeholder">`). 가짜 URL 금지.
- **신규 안티패턴 2종** — `unsourced-fact` (출처 없는 구체 사실), `fake-image-url` (검증 없는 이미지 URL). 각각 양성/음성 예시 5개 + BLACK 재작성 지시 템플릿 + 적용 카테고리 명시.
- **BLACK 도구 확장** — `agents/roasting-black.md`의 tools에 `WebSearch`, `WebFetch` 추가. 1차 출처 확보용.

### Changed

- **안티패턴 검출 룰** 5종 → 7종으로 확장. `Phase 4` 본문·참조 인덱스에 신규 룰 노출.
- **SKILL.md Phase 3** — BLACK 호출 시 fact-grounding/이미지 활성화 신호 감지 절차 명시. 도메인 신호가 있으면 BLACK 프롬프트에 "fact-heavy 모드" 라벨링.

## [0.4.4] - 2026-05-17

### Changed

- **세션 폴더 명명 규칙** — `{YYYYMMDD-HHMMSS}-{tmpid}` → **`{YYYYMMDD}_{NN}`** (예: `20260517_01`). 그날 N번째 작업물이 한눈에 보이도록 단순화. NN은 그날 `output_dir/` 안의 기존 `{YYYYMMDD}_*` 폴더를 스캔해 max+1로 결정, 2자리 zero-padding (100개 이상이면 자동 3자리 확장).
- **시작 시각 보존** — 폴더명에서 시각 정보가 빠졌으므로 `{session_dir}/meta.json`에 `{"started_at": "ISO-8601", "session_id": "..."}`를 Phase 0에 저장. Phase 7 소요 시간 계산은 meta.json에서 읽음.
- **Phase 7 deliver 경로 안내** — 산출물 경로를 항상 session_id 폴더명 포함 전체 경로로 표시 (예: `~/Desktop/Roasting/20260517_01/final/output.html`). 사용자가 그날 N번째 작업물을 즉시 식별 가능.

## [0.4.3] - 2026-05-17

### Added

- **Phase 7 표준 완료 푸터 통일** — 모든 호출의 deliver 메시지에 세 가지 메타 항목을 강제로 포함: **소요 시간**(세션 시작부터 deliver 시점까지 `N분 M초`), **주요 업무 한 줄**(`{case_id} · {라운드}라운드 · 평균 {score}` + 합격/강제 종료 아이콘), **카카오톡 발송 여부**(`mcp__*__KakaotalkChat-MemoChat` 도구 등록 시 자동 발송 후 `📱 발송됨`, 미연결 시 `스킵`). 이전엔 사용자가 명시적으로 요청해야 표시되던 항목들을 표준화. 메시지 본문은 200자 이내 압축.

## [0.4.2] - 2026-05-17

### Added

- **사용자 출력 폴더 지원** — `~/.claude/roasting/config.json`의 `output_dir` 필드로 모든 호출의 산출물 저장 위치 지정 가능. 예: `{"output_dir": "~/Desktop/Roasting"}`로 두면 매 호출마다 `~/Desktop/Roasting/{session_id}/`에 input·round-N·final 전체 세션이 저장됩니다. config 없거나 필드가 빈 문자열이면 기존 디폴트(`~/.claude/roasting/_workspace/{session_id}/`) 그대로. 향후 필드 확장(예: `default_slide_template`, `telemetry`)을 위해 객체 구조 유지.

### Changed

- **SKILL.md 산출물 경로 추상화** — 본문의 하드코딩된 `~/.claude/roasting/_workspace/` 경로를 `{session_dir}`(Phase 0에서 결정)로 일관 교체. Phase 3 BLACK draft 출력, Phase 4 strikes.json, Phase 7 final/ 모두 단일 변수 참조.
- **디스크 풀 폴백 표 갱신** — `output_dir`이 사용자 폴더(예: Desktop)일 때는 자동 삭제하지 않고 사용자에게 알림 후 중단. 디폴트 `_workspace`에서만 가장 오래된 5개 자동 삭제.

## [0.4.1] - 2026-05-17

### Changed

- **버전 bump (no functional changes)** — v0.4.0 동일 워크플로우·동일 통합. plugin.json·SKILL.md·output-formats.md의 버전 라벨만 0.4.1로 일치.

## [0.4.0] - 2026-05-17

### Added

- **taste-skill 외부 통합** (Leonxlnx/taste-skill) — 디자인 산출물(HTML 페이지·웹사이트·랜딩·슬라이드·이미지·로고·브랜드 키트)에 anti-slop 프론트엔드 프레임워크를 자동 enrich. 8개 디자인 케이스(c41/42/43/45/c59/c70/c73/c74) frontmatter에 `enrich` 블록 추가. 변형 자동 선택 로직으로 `design-taste-frontend`(기본 HTML) / `high-end-visual-design`(프리미엄 톤, c70 보강) / `minimalist-ui` / `industrial-brutalist-ui` / `imagegen-frontend-web` / `imagegen-frontend-mobile` / `brandkit`(c59·로고·아이덴티티) / `full-output-enforcement` 중 1순위 변형을 메인 Claude가 입력에서 추론해 호출. generic_case 폴백 + HTML 요청 시에도 자동 적용. 미설치 시 graceful degradation + 1회 설치 안내(`npx skills add https://github.com/Leonxlnx/taste-skill`). 신규 `design_artifact_detected` `when` 조건 추가.
- **`assisted` 빌더 모드 신설** — generic_case 폴백 + 사용자가 HTML/페이지/대시보드/일정표/카드 등 디자인 산출물을 요청할 때 자동 진입. 슬라이드 라이브러리 35종 중 1개를 베이스로 고른 뒤 BLACK이 콘텐츠 주입 + 필요한 인터랙티브 요소(탭·필터·접힘·간단 차트)만 보강. 처음부터 자체 디자인 생성은 금지 (= `direct` 영역 침범). HTML 빌더 모드는 이제 4종: `slides | landing | direct | assisted`.
- **generic 페르소나 프로파일** — Phase 1 §5 폴백에서 케이스 시드가 없을 때 사용할 BLACK·RED·SILVER·BLUE·GOLD 5인 기본 캐스팅을 명시. 입력에서 도메인·산출물 유형·사용 시점·결정자를 자체 추론해 5색 채점 워크플로우를 그대로 유지.
- **케이스 프론트매터 `html_mode` 필드** — `c41`·`c42`·`c43`·`c45`·`c70`·`c73`에 `output_format` / `html_mode` / `slide_template_pool` / `default_formality` 필드 추가. SKILL.md는 이 필드를 단일 진실로 참조하고 케이스 ID 하드코딩을 제거. 향후 HTML 케이스 추가는 케이스 파일만 수정해도 동작.

### Changed

- **Phase 1 §5 폴백 워크플로우 강제** — 라우팅 신뢰도 < 0.5(generic_case)라도 Phase 3 BLACK 서브에이전트·Phase 5 RGSB 4인 채점·9.5 게이트·Phase 7 3종 산출물 출력을 단축 없이 그대로 실행. "자산 시드 없으니 한 번에 출력" 같은 단축을 명시적으로 금지. v0.3 세션에서 폴백 모드가 워크플로우를 통째로 스킵하던 사고의 재발 방지.
- **SKILL.md ↔ 구현 일관성 정리 (갈래 B)** — `scripts/route.py`·`scripts/build_slide_html.py`·`scripts.invoke_skill`·`scripts.anti_patterns.detect_all`·`scripts.deliver.deliver()` 등 실재하지 않던 Python 호출 묘사를 "Claude 절차 — Python 스크립트 없음. 메인 Claude가 직접 수행"으로 라벨링하고 절차 산문으로 교체. 의사코드 블록은 "참고용 의사코드 (Claude가 동일하게 수행)"로 명시.
- **`enrich` 호출 경로 정정** — `scripts.invoke_skill.invoke()` stub 묘사를 메인 Claude의 `Skill` 도구 직접 dispatch 절차로 교체. 사용자 환경에 스킬 미설치 시 조용히 graceful degradation.
- **컨펌 시점·에러 폴백 표** — `slides`·`landing`·`assisted` 3-mode 세트로 슬라이드 ID 선택 트리거를 확장. 라우팅 신뢰도 < 0.5와 영어 입력 폴백은 "Phase 1 §5 동일 절차"로 정리.

## [0.3.0] - 2026-05-17

### Added

- **2 new remote cases synced from airoasting.github.io/5color** — `c73 웹사이트 제작` (folio VII·3, 마케팅 · 단일 HTML 직접 출력) + `c74 이미지 제작` (folio VII·4, 마케팅 · 7단 프롬프트 세트). 사이트 측에서 신설된 케이스를 그대로 흡수.
- **`direct` 빌드 모드** in `scripts/build_slide_html.py` — `DIRECT_HTML_CASE_IDS = {"c73"}`. BLACK이 작성한 단일 HTML 파일을 템플릿 fetch 없이 `output.html`로 그대로 통과시킨다. PPT/c70과 달리 인라인 CSS·시맨틱 마크업·반응형을 BLACK이 자급.
- **`c73` `direct` 모드용 BLACK 헤딩 규약** (`agents/roasting-black.md`) — 헤딩 분할 없음, `<!doctype html>`부터 완성, 외부 CDN/이미지 URL 금지.
- **Routing phrasings 6개 추가** — 신규 c73·c74(웹사이트·이미지) 각 3종. 라우팅 테스트셋 198 → 204.

### Changed

- **64개 케이스 subhead 전면 리라이트** — 5color 사이트에서 "다섯 사람이 ~ 같이 다듬어 드립니다" 패턴을 더 짧고 단정한 "한 호흡, 한 메시지" 스타일로 교체. `sync_cases.py`로 idempotent 갱신.
- **ID 재할당 (Breaking, but internal):** 로컬에서만 존재하던 `c73 DART 회사 분석` → `c75`로 이동(folio IV·20), `c74 전략 프레임워크 메모` → `c76`(folio V·7)로 이동. 이유 — 5color 사이트의 신규 c73·c74가 마케팅 카테고리(웹사이트·이미지)에 배정되면서 ID 충돌. enrich 블록(/dart, /strategy)은 보존.
- **`c70` folio** `VII·3` → `VII·5` — 신규 c73 웹사이트 제작과 folio 충돌 해소.
- **케이스 총량** 66 → 68 (5color 64 + 로컬 확장 4: c41·c70·c75·c76).
- **SKILL.md** Phase 2 — HTML 산출물 케이스 분기를 `slides`·`landing`·`direct` 3-mode 모델로 재구성. `mode_for_case()`가 단일 진실.
- **`output-formats.md`** — `direct` 모드 행 추가, c74 이미지(마크다운 7단) 행 추가, c75 DART/c76 전략 ID 정정.
- **enrich 매핑** (SKILL.md ecosystem 테이블) — `/dart`는 `c75`, `/strategy`는 `c76`을 가리키도록 정정.
- **`sync_cases.py` 도크스트링** — "63 cases" → "64 cases" + 로컬 확장 케이스 정책 명시.
- **`plugin.json` description** — 66 → 68, 신규 케이스(image-prompt set, hand-coded website, DART company brief, strategy memo) 노출, c73 `direct` HTML 동작 명시.

### Documentation

- **SKILL.md 예시 테이블** — 신규 c73(웹사이트 직접 HTML) + c74(이미지 프롬프트) 입출력 사례 추가, c75/c76 ID 정정.

## [0.2.1-unreleased] - 2026-05-15

### Added

- **New case `c70` 웹사이트·랜딩페이지** (folio VII·3 → 0.3.0에서 VII·5, 마케팅) — 한 화면 한 메시지·CTA 한 개 합격선의 랜딩페이지 케이스. BLACK = 그로스 마케팅·랜딩 UX 카피라이터 17년차+. RGSB는 가치제안 한 줄(RED), 정보 위계·CTA 반복(SILVER), 모바일 첫 5초 호흡(BLUE), SNS 광고 클릭 시나리오(GOLD)로 채점.
- **`build_slide_html.py` landing 모드** — H2 단위로 BLACK Markdown을 랜딩 섹션(히어로·소셜프루프·기능·CTA·FAQ)으로 분할하고 slide_library 템플릿 컨테이너에 주입. PPT 모드(슬라이드 단위 H1)와 같은 fetch + container 로직을 공유하고 콘텐츠 블록 셰이프만 다름.
- **`mode_for_case()` 헬퍼** + `LANDING_CASE_IDS` frozenset — case_id → builder 모드 매핑이 한 곳에 모임. 차후 HTML 산출물 케이스 확장 시 이 함수만 갱신.
- **Phrasings 3개 추가** (c70 natural/keyword/audience) — 라우팅 테스트셋 195 → 198.
- **단위 테스트 4개** — landing 분할, H2 미존재 폴백, mode_for_case 라우팅, build() e2e mock.

### Changed

- **SKILL.md Phase 2** — "PPT 카테고리" 분기를 "HTML 산출물 케이스 (c41/42/43/45/c70)"로 통합. 모든 HTML 산출물은 slide_library 35개 중 가장 적정한 1개를 그대로 베이스 HTML로 사용. 자체 디자인 생성 금지.
- **`output-formats.md` 마케팅 행 분할** — c70은 HTML, 나머지 2개(c56·c59)는 Markdown.
- **`scripts/deliver.py`** — `mode=mode_for_case(case_id)` 인자로 빌더 호출, 라우팅·빌드 일관.
- **`plugin.json`** — case count 63 → 66, description에 landing-page 추가.

### Documentation

- **README.md / README.ko.md 전면 개편** (v2). 5-Color critique 결과를 직접 적용해 9.5 합격선 위로 끌어올림.
  - **방법론 특성 6가지** 섹션 신설 (case별 캐스팅·GOLD는 평가자가 아닌 독자·의도적 의견 분기·9.5 숫자 합격선·사전 안티패턴 검출·66 case 자체가 IP).
  - **다른 하네스 패턴과의 비교표** (Director-Critic·Self-Refine·Multi-Agent Debate·Constitutional AI·Producer-Reviewer·RLHF).
  - **3-tier 합격선 표** (9.0 / 9.5 / 9.7군의 이유).
  - **예시 산출물 + 실패 보고 박스** (한국어 본문 6줄 BLACK 출력 + 9.5 미달 시 사유 보고 샘플).
  - **검증된 품질 지표 표** (라우팅 98.4% · false positive 0% · 101/101 tests · quality avg 9.17).
  - **케이스별 BLACK 캐스팅 예시 표** (영문 README 미러링).
  - 영문 README "Korean only" → "Korean cases, universal pattern"으로 reframe (글로벌 개발자에게 reference architecture로 재제시).
  - em dash 17개 (영문 11 + 한국어 6) 모두 제거 (5-Color 자체 fail 룰 통과).
  - 한국어판 주술 정합·번역체 제거 추가 폴리시.

## [0.2.0] - 2026-05-10

### Added

- **Enrich field for case definitions** — cases can now declare `enrich:` to invoke other Claude Code skills (`/dart`, `/strategy`) for automatic context enrichment before BLACK draft.
- **2 new cases** — `c73 DART 기반 회사 분석 리포트`, `c74 전략 프레임워크 적용 메모`.
- **9 existing cases enriched** — c25, c28, c29, c31, c33, c34, c37, c40, c45 now declare optional `/dart` and/or `/strategy` enrichment.
- **scripts/invoke_skill.py** — stub for cross-skill invocation; full runtime integration ships in v0.3.

### Changed

- `scripts/sync_cases.py` preserves `enrich:` field on resync.
- Routing test set expanded from 189 to 195 phrasings.

### Privacy / Backward compatibility

- `enrich:` is opt-in and gracefully degrades. /roasting works exactly as v0.1 if `/dart` and `/strategy` are not installed.

## [0.1.0] - 2026-05-10 (Open Beta)

### Added

**Core pipeline (7-Phase):**
- Phase 0: Session initialization and workspace setup (`_workspace/{session}/`)
- Phase 1: Expert Pool routing — Haiku judge maps user request → top-3 case IDs from 63-case index
- Phase 2: Case seed load — lazy-loads per-case `.md` from `references/cases/`; slice limits managed
- Phase 3: BLACK draft — role-cast producer writes first artifact per case BLACK persona
- Phase 4: Anti-pattern detection — 5 detectors run before every review round
- Phase 5: RGSB review — Agent Teams primary path (TeamCreate + SendMessage + TaskCreate);
  sub-agent fallback retained for stability
- Phase 6: Loop — 4-round cap; debate triggers at σ ≥ 0.5 between any two reviewer scores
- Phase 7: Deliver — polished artifact + score sheet + slide deck (PPT cases)

**Case library (63 cases, 8 categories):**
- 외부 커뮤니케이션 (12): email, apology, crisis message, press release, newsletter, case study,
  launch message, FAQ, CS template, vision/mission, lecture deck, pitch deck, keynote
- 소셜미디어·글쓰기 (9): LinkedIn post, SNS post, blog, newspaper column, AI text polish,
  fiction, poetry, LinkedIn profile, newsletter
- 내부 커뮤니케이션 (7): company notice, job posting, difficult message, town hall, HR policy,
  1on1, workshop materials
- 분석·보고서 (12): 1-page report, meeting minutes, board report, shareholder letter, PRD,
  quarterly review, IR presentation, OKR report, investment memo, market analysis,
  expert call note, management diagnosis, narrative memo, analysis report
- 의사결정·전략 (10): business proposal, sales proposal, board report, shareholder letter,
  PRD, executive PPT, storyline, consulting deck, narrative memo
- 법무 검토·규제 대응 (7): contract review, legal opinion, complaint/answer, brief,
  audit opinion, tax opinion, due diligence, internal control report
- 마케팅 (2): copy/naming, brand guidelines
- 커리어·상담 (4): resume, cover letter, interview prep, leadership counseling

**5-Color reviewer team:**
- BLACK: Sonnet-powered producer, role-cast to case BLACK persona
- RED (이성): logic and intent clarity reviewer
- SILVER (분야 전문가): domain structure specialist
- BLUE (공감): tone, length, and empathy reviewer
- GOLD (독자 시나리오): reader scenario simulation

**Anti-pattern detection (5 types):**
- `HALLUCINATED_NUMBER`: regex extraction + Haiku source verification; exempt on c63/c64/c69
- `VAGUE_CTA`: regex sieve on last 50 chars + Haiku confirm; ~30 applicable cases
- `MISSING_GOLD_HOOK`: Haiku judge, first 200 chars vs case GOLD scenario
- `TONE_MISMATCH`: Haiku, tone match score < 6 threshold
- `LEGAL_RISK_TERM`: regex-only; legal + external comms categories
- 3-strikes counter: same pattern 3× in a row → escalate to user

**PPT / slide_library integration:**
- 35 slide templates indexed by color axis (professional/creative) × formality axis
- BLACK writes HTML deck; fallback to Markdown if template load fails
- Template confirmation flow on first call for PPT cases

**Scoring and acceptance:**
- RED·SILVER·BLUE 3-reviewer average threshold: 9.5 / 10
- GOLD reader immersion threshold: 9.5 / 10
- 4-round cap; debate auto-triggers at σ ≥ 0.5
- Score scale: 10=flawless, 9.5=pass, 9=one fix, 8=v2 candidate, ≤7=rewrite

**Telemetry and feedback:**
- Anonymous opt-in telemetry (default OFF); Supabase backend, INSERT-only RLS
- Fields: user_id (local UUID), case_id, final_score, round_count, cost estimate,
  anti_patterns_detected, debate_triggered, completion_status, timestamp
- Content (input, BLACK output, RGSB comments) never transmitted
- `/roasting --feedback`: opens pre-filled GitHub Issue with session metadata

**CLAUDE.md auto-registration:**
- `install_hook.py` registers `/roasting` pointer in `~/.claude/CLAUDE.md` on install

**Developer tooling:**
- `Makefile` targets: sync-cases, sync-slides, gen-case-catalog, test, lint, typecheck,
  package, publish, clean
- `scripts/sync_cases.py`: HTML parser for airoasting.github.io/5color (brace-counting
  state machine; no external JS engine required)
- `scripts/gen_case_catalog.py`: generates `docs/ko/case-catalog.md` from case frontmatter
- `scripts/route.py`: Haiku-backed Expert Pool router + Wilson 95% CI helper
- `scripts/anti_patterns.py`: 5 detectors + StrikeCounter
- `scripts/llm_judge.py`: HaikuJudge + fake_judge fixture for CI
- `scripts/telemetry.py`: Supabase async client + local config reader
- `scripts/deliver.py`: artifact + score sheet + HTML deck assembler
- `scripts/feedback.py`: GitHub Issue URL builder
- `scripts/build_slide_html.py`: HTML deck renderer from template JSON

**CI (GitHub Actions):**
- `test.yml`: lint (ruff + mypy), unit (no slow/network), network (main push only)
- `release.yml`: tests + `make package` + GitHub release on `v*` tag; prerelease
  auto-detected from tag name containing `-`

**Tests:**
- 50 anti-pattern unit tests (10 per detector + 5 strike counter; fake_judge in CI)
- 189 routing accuracy tests (63 cases × 3 natural-language phrasings); top-1 Wilson
  95% LB ≥ 0.90 gate

### Privacy

- User input prompt, BLACK draft, RGSB comments, and rendered output are **never** transmitted.
- Telemetry default = OFF; opt-in via `~/.claude/roasting/config.json`.
- Full policy: [docs/PRIVACY.md](docs/PRIVACY.md)

### Known limitations (v0.1 beta)

- Agent Teams path (Phase 5) uses experimental Anthropic feature; auto-falls back to
  sequential sub-agent dispatch on error.
- Case sync (`make sync-cases`) is manual; no automatic update on 5color site changes.
- HTML-only slide output; PPTX export planned for v0.2.
- Korean-language only; English input not optimized.

---

## v0.2 (planned)

- Instinct mode: fast single-reviewer path
- User-configurable Hooks for custom anti-pattern rules
- Automatic case sync with 5color site webhook
- Case validation tier labels (verified / beta)
- PPTX direct export
