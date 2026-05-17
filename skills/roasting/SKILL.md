---
name: roasting
description: 한국어 화이트칼라 산출물(이메일·보고서·PPT·웹사이트·이미지 프롬프트·랜딩페이지·이사회 메모·IR 자료·계약 검토·이력서·사내 공지 등 68개 케이스)을 5-Color Harness로 작성합니다. 한국 비즈니스 리더가 "써줘·다듬어줘·만들어줘·검토해줘·정리해줘" 같은 자연어 요청을 하거나 `/roasting xxxxx`로 호출하면 자동으로 케이스를 골라 BLACK 작성+RGSB 4인 채점(9.5 합격선, 4라운드)으로 산출물·평가·결정 로그를 만듭니다. PPT·랜딩페이지 케이스는 slide_library 템플릿 자동 결합, 웹사이트 제작 케이스는 단일 HTML 직접 출력. 한국어 전용. 영어 입력은 일반 모드 폴백.
---

# /roasting — 5-Color Harness Execution Engine

5color 사이트의 64개 케이스 + 4개 로컬 확장 케이스(c41 임원 PPT · c70 랜딩페이지 템플릿 결합 · c75 DART 회사 분석 · c76 전략 프레임워크 메모) = 총 68개 케이스를 Claude Code 위에서 *집행*하는 엔진. 임원이 자연어 한 줄로 호출하면, 7-Phase 워크플로우(Pipeline + Supervisor 패턴, Phase 5만 Agent Teams)로 산출물·평가·결정 로그 3종을 출력한다.

## 핵심 원칙

1. **단일 진입**: `/roasting xxxxx` 한 줄만 학습. 도메인은 자동 라우팅.
2. **Progressive Disclosure**: 케이스 1줄 인덱스만 항상 컨텍스트, 매칭 시 케이스 풀 정의 로드.
3. **5-Color 본래 의도 충실**: 4인 RGSB가 *서로 토론* (σ ≥ 0.5 자동 트리거).
4. **콘텐츠 0 수집**: telemetry는 메타데이터만. xxxxx·산출물·코멘트는 외부 전송 0.
5. **결정적 비용**: 5명 × 4라운드 cap × 케이스 정의 고정 = 호출당 ~$0.36.

## 워크플로우 (7 Phase)

### Phase 0 — 진입과 세션 초기화

트리거 시:
1. **출력 폴더 결정:**
   - `~/.claude/roasting/config.json` 존재 여부 확인.
   - 존재하고 `output_dir` 필드가 비어있지 않으면 → `output_dir` 사용 (사용자가 선택한 폴더, 절대 경로 또는 `~` 시작).
   - 그 외 (config 없음·필드 없음·빈 문자열) → 디폴트 `~/.claude/roasting/_workspace/` 사용.
   - 경로의 `~`는 사용자 홈으로 확장. 경로가 존재하지 않으면 `mkdir -p`로 생성.
2. **세션 ID 결정 (`{YYYYMMDD}_{NN}` 형식):**
   - 오늘 날짜 `YYYYMMDD`(예: `20260517`)를 구한다.
   - `{output_dir}/` 안에서 `{YYYYMMDD}_*` 패턴 폴더를 모두 스캔.
   - 가장 큰 `NN`을 찾아 +1. 없으면 `01`.
   - 2자리 zero-padding. 100개 이상이면 자동 3자리로 확장.
   - 예: `20260517_01`, `20260517_02`, ... 그날 99개 넘으면 `20260517_100`.
3. 세션 디렉토리 생성: `{output_dir}/{YYYYMMDD}_{NN}/`. 이 폴더를 `session_dir`로 모든 후속 Phase가 공유.
4. `{session_dir}/input.txt`에 xxxxx 저장.
5. **시작 시각 저장:** `{session_dir}/meta.json`에 `{"started_at": "ISO-8601 시각", "session_id": "{YYYYMMDD}_{NN}"}` 기록. Phase 7 소요 시간 계산에 사용.

#### config.json 스키마

```json
{
  "output_dir": "/Users/your_name/Desktop/Roasting"
}
```

- `output_dir`: 절대 경로 또는 `~` 시작 상대 경로. 비우거나 키 자체를 생략하면 디폴트 사용.
- 향후 필드 확장 여지(예: `default_slide_template`, `telemetry`)를 위해 객체 구조 유지.
- 설정 변경은 즉시 다음 호출부터 반영. 진행 중인 세션은 영향 없음.

사용자에게 노출되는 모든 산출물 경로(`/roasting --feedback` 안내, Phase 7 deliver 메시지 등)는 결정된 `session_dir`을 사용한다.

### Phase 1 — PARSE (Expert Pool 라우팅)

목적: xxxxx → 66 케이스 중 1개 매칭.

처리:
1. `references/cases/_index.md` 로드 (~30KB).
2. 라우팅 (Claude 절차 — Python 스크립트 없음): 메인 Claude가 `_index.md`의 1줄 케이스 설명 68개와 사용자 입력을 비교해 top-3 케이스 후보와 0~1 신뢰도를 자체 판정한다. 의도 거리·도메인 일치·산출물 유형 일치를 종합. 같은 입력은 같은 결과가 나오도록 보수적으로 판단한다.
3. `routing.json` 저장: `{top3, confidence, selected_case_id}`.
4. **분기:**
   - 신뢰도 ≥ 0.85 → top-1 자동 선택, Phase 2로.
   - 신뢰도 < 0.85 → 사용자에게 top-3 보여주고 1턴 confirm.
5. **에러 폴백 (generic_case):** 모든 후보 신뢰도 < 0.5 → generic 5-Color 모드로 진행. 케이스 시드는 없지만 **워크플로우는 단축하지 않는다**.

   **필수 강제:**
   - Phase 3 BLACK 서브에이전트 호출 필수. 메인 Claude가 직접 산출물을 쓰면 워크플로우 위반.
   - Phase 5 RGSB 4인 채점 필수. 평균 9.5 게이트 동일 적용.
   - Phase 6 라운드 루프 (최대 4) 동일 적용.
   - Phase 6.5 한국어 검증 패스 + Phase 7 4종 산출물 (`output.*` · `critique.md` · `reasoning.md` · `korean-polish.md`) 동일 생성.

   **generic 페르소나 프로파일 (케이스 시드 부재 시 캐스팅):**
   - **BLACK:** 범용 작성자 (산출물 유형은 xxxxx에서 추론 — 일정·계획·정리·노트·웹 페이지 등). 입력에서 영역·톤·분량을 자기 판단으로 잡는다. em dash 0회·종결 체 일관성·번역투 금지는 공통.
   - **RED (이성):** 논리·근거·구조 정합성 검증자. "결론이 한 줄로 잡히는가, 근거가 결론을 받치는가."
   - **SILVER (분야 전문가):** 입력에서 추론된 도메인의 일반 베테랑. "이 분야의 관행·디테일·정보 위계가 맞는가."
   - **BLUE (공감):** 실제 독자/사용자의 호흡과 가독성 비평. "독자가 이 산출물을 처음 만났을 때 어디서 멈추는가."
   - **GOLD (독자 시나리오):** 실제 사용 장면 시뮬레이션. xxxxx에서 사용 시점·장소·결정자를 합리적으로 구성하고 그 장면에서 합격선을 본다.

   **사용자 알림 (1회, Phase 0 직후):**
   > 이 요청은 케이스 라이브러리(68 케이스) 매칭에 실패해 generic 5-Color 모드로 진행합니다. BLACK 1인 + RGSB 4인 채점 + 9.5 게이트는 동일하게 적용됩니다.

   **출력 포맷 추정:**
   - 사용자 입력에 "HTML·페이지·웹·랜딩·대시보드·일정표·카드·인터랙티브·탭·필터" 같은 신호가 있으면 → 출력 포맷 `html`, 빌더 모드 `assisted` (Phase 2가 슬라이드 템플릿 1개 자동 선택).
   - 사용자 입력에 "이미지·사진·로고·브랜드·시각·hero shot" 같은 신호가 있으면 → 출력 포맷 `md` (7단 이미지 프롬프트 세트, c74 톤 차용).
   - 그 외 → 출력 포맷 `md`, Markdown 본문.

   **taste-skill 자동 enrich (디자인 산출물일 때):**
   - 출력 포맷 `html` 또는 이미지/로고/브랜드 신호 감지 시 → `design_artifact_detected` = True.
   - "Design Taste Integration" 절의 변형 자동 선택 로직에 따라 1순위 변형(`design-taste-frontend`/`brandkit`/`imagegen-frontend-web` 등)을 `Skill` 도구로 호출, 결과를 Phase 3 BLACK 프롬프트에 첨부.
   - 미설치 시 조용히 스킵.

   **금지 (재발 방지):**
   - Phase 3·5 생략하고 메인 Claude가 산출물 직접 작성.
   - "자산 시드 없으니 한 번에 출력" 같은 단축.
   - 채점 없이 즉시 사용자에게 결과 전달.
   - generic_case + HTML 요청에서 슬라이드 템플릿 선택 없이 자체 디자인 처음부터 생성 (= `direct` 모드 영역 침범).

### Phase 2 — SEED LOAD

목적: 케이스 정의 + 슬라이드 템플릿 + 케이스 적용 안티패턴 로드.

처리:
1. `references/cases/{case_id}.md` 로드 (BLACK + RGSB 페르소나 정의 + GOLD 시나리오).
2. **HTML 산출물 케이스 추가 처리 (4가지 빌더 모드):**
   - 출력 포맷이 `html`로 잡히는 케이스는 빌더 모드가 넷이다 — `slides | landing | direct | assisted`.
   - **단일 진실:** 모드는 케이스 프론트매터의 `html_mode` 필드를 그대로 읽는다. Claude는 ID를 하드코딩하지 않는다. `references/cases/{case_id}.md`의 frontmatter에 `html_mode: slides|landing|direct|assisted`를 찾는다. 필드가 없으면 → `slides`로 폴백.
   - **`slides` 모드:** `references/slide-templates/index.json` 35개 템플릿 중 톤·formality·color에 **가장 적정한 1개**를 골라 그대로 베이스 HTML로 사용. 슬라이드 컨테이너에 BLACK 산출물을 슬라이드 단위(H1·H2)로 주입.
   - **`landing` 모드:** 동일하게 35개 템플릿 중 1개를 골라 베이스 HTML로 사용. 차이는 분할 방식 — H2 단위로 랜딩 섹션(히어로·소셜프루프·기능·CTA·FAQ 등)을 주입.
   - **`direct` 모드:** BLACK이 직접 작성한 단일 HTML 파일(인라인 CSS·시맨틱 마크업·반응형)을 그대로 `output.html`로 출력. 템플릿 fetch도, 컨테이너 주입도 없다. 자체 디자인 생성이 본질.
   - **`assisted` 모드:** generic_case 폴백 + 사용자가 HTML 요청 시 자동 진입. 35개 템플릿 중 1개를 골라 베이스 HTML로 사용하되, BLACK이 콘텐츠 주입 + 필요 시 인터랙티브 요소(탭·필터·접힘·간단 차트) 보강 허용. 자체 디자인 시스템 처음부터 생성 금지. 상세는 `references/output-formats.md` "assisted 모드" 절 참조.
   - `slides`·`landing`·`assisted` 모드는 슬라이드 ID 선택 필수. `direct` 모드는 무의미하므로 이 단계 건너뜀.

#### 2-2. 슬라이드 템플릿 선택 프로세스 (top-3 → 1순위 1개)

**핵심 원칙: 자동 패스 금지. 모든 호출에서 반드시 top-3 후보를 추출하고, 그 중 최적 1개를 선택해 사유를 reasoning.md에 기록한다.** preferences를 곧장 자동 적용하면 디자인 선정이 블랙박스가 되어 사고 원인 추적이 불가능하다.

```
1. Phase 2 진입 시 항상 35종 템플릿 인덱스(references/slide-templates/index.json) 전체 로드.

2. 메인 Claude가 다음 4개 축으로 입력을 분석:
   - 도메인 (여행·재무·강의·랜딩·매뉴얼 등)
   - 톤 (formal · neutral · casual)
   - color preference (light · dark · mixed)
   - 산출물의 핵심 인상 (편안함 · 권위 · 매거진 · 실험적 등)

3. 35종 각각에 적합성 점수 1~10 계산 (도메인 키워드 일치 가중치 가장 큼).

4. top-3 후보 추출. 동점 시 formality 우선, 다음 color, 다음 slide_count.

5. preferences 처리:
   - {output_dir 또는 ~/.claude/roasting}/preferences/{case_id}.json 또는 generic_case.json 확인
   - preferences가 top-3 안에 있으면 → 그것을 1순위로 (지속성 우선)
   - preferences가 top-3 밖이면 → 사용자 입력이 이전과 톤이 달라졌다는 신호로 해석. top-3 점수 1위를 1순위로 채택하고 preferences 갱신 후보로 표시.

6. 1순위 + 2·3순위 + 각각 선택 사유 한 줄을 reasoning.md의 'Slide Template Selection' 절에 기록. 이 절은 모든 HTML 산출물에 반드시 존재.

7. 사용자에게 1줄 알림(부담 0턴):
   "디자인 템플릿: [tri-color-magazine] 선택 (top-3: tri-color-magazine · soft-classic · earth-archive). 다른 선호 있으시면 알려주세요."

8. 사용자가 명시적으로 "다른 거"를 요청하면 2순위로 교체, preferences 갱신.

9. 결정 직후 BLACK 호출 시 슬라이드 템플릿 URL을 BLACK 프롬프트에 명시. BLACK은 그 URL을 WebFetch로 받아 베이스로 사용 (agents/roasting-black.md "HTML 산출물 베이스 룰" §1 강제).
```

**금지 (재발 방지):**
- preferences가 있다고 top-3 추출을 스킵.
- 1순위 선택 사유를 reasoning.md에 기록하지 않음.
- BLACK이 슬라이드 템플릿을 WebFetch하지 않고 자체 인라인 CSS만 작성.
- **`<deck-stage>` 태그 또는 `deck-stage.js` 스크립트 로드.** 둘 다 실재하지 않는 404·환각 룰. 진짜 베이스 룰은 `<div class="deck">` + `<div class="slide">` + `max-width: 1200px` + `aspect-ratio: 16/10` + `container-type: inline-size` + `cqi` 단위. 상세는 `agents/roasting-black.md` "HTML 산출물 베이스 룰".
- **HTML 슬라이드에 `width: 1920px` 또는 `height: 1080px` 고정.** 화면 깨짐 원인. aspect-ratio + cqi 단위로 대체.

이 절차는 매 호출마다 30초 추가되지만 디자인 품질 일관성 + 디버깅 가능성이 결정적으로 올라간다.
3. 케이스 카테고리 따라 `references/anti-patterns/*.md` 중 적용 항목만 로드.
4. `case-context.json` 저장.

#### 2-3. 입력 사전 처리 (Pre-Processing Pack)

**핵심 원칙: BLACK 호출 전에 메인 Claude가 사용자 입력의 빈칸·날짜·1차 출처를 미리 처리해 패키지로 박아준다.** BLACK이 입력 정합성을 자체 판단하면 (a) 상대 날짜 → 요일 환산을 빠뜨리거나 (b) 누락 파라미터(인원·예산·출발지·취향)에 자기 가정을 박지 않아 GOLD가 R1에서 "결정 못 하는 빈칸"으로 깎고 (c) fact-heavy 입력에서 2차 출처(블로그·KKday)만 보고 작성해 SILVER가 R1에서 사실 디테일로 깎는 패턴이 반복된다. R1 평균을 9.0+로 끌어올리기 위해 사전 처리를 의무화한다.

처리 (메인 Claude가 BLACK dispatch 직전에 수행):

1. **날짜·시간 정합성 패키지.**
   - 사용자 입력에 상대 날짜(다음주 금요일 / 이번 주말 / 다음달 첫째 주 / D-5)가 있으면 → 오늘 날짜를 기준으로 절대 날짜·요일로 환산. 결과를 `dates_resolved`로 저장.
   - 예: 오늘 2026-05-17(일) + "다음주 금요일부터 일요일까지" → `{"start": "2026-05-22 (Fri)", "end": "2026-05-24 (Sun)", "nights": 2}`.
   - 환산 결과를 reasoning.md "Pre-Processing Pack" 절에 기록.

2. **누락 파라미터 기본값 + 명시 라벨.**
   - 산출물 유형에 따라 결정에 필요한 핵심 파라미터를 미리 점검. 누락 시 합리적 기본값을 잡고 BLACK 입력과 산출물 표지에 **명시 라벨**로 박는다.
   - 예시:
     - 여행 일정: 인원(기본 1인) · 출발지(한국 사용자면 ICN) · 예산 레벨(미드~프리미엄) · 동반자 유형
     - 회사 분석: 분기 기준 · 비교 기간(전년 동기 vs 직전 분기) · 산업 카테고리
     - 영업 덱: 청중 인원수 · 발표 시간 · 의사결정자 직급
   - 기본값을 박은 모든 파라미터는 산출물 1슬라이드 또는 첫 단락에 라벨로 노출(예: "1인 기준 (2인 시 ±20%)"). GOLD가 R1에서 "1인/2인 분기"로 깎는 패턴을 사전 차단.

3. **1차 출처 화이트리스트 (fact-heavy 케이스 한정).**
   - fact-grounding 활성화된 입력에서, 도메인별 1차 출처 화이트리스트를 BLACK 프롬프트에 박는다. BLACK은 2차 출처(블로그·KKday·여행 카페·일반 검색 요약)는 보조로만 쓰고, 화이트리스트 출처를 먼저 시도한다.
   - 도메인별 화이트리스트 예시 (BLACK이 가능한 한 우선 시도):
     - 항공·공항: 항공사 공식 / 공항공사 / 국토부
     - 일본 여행 교통: 난카이/JR 공식 · 일본 관광청
     - 한국 외 비상연락처: 외교부 영사콜센터 · 재외공관
     - 회사 재무: DART · IR 공식 / SEC EDGAR / 각국 금감원 공시
     - 통계·인구: 통계청 KOSIS / OECD / World Bank
     - 기상: 기상청 / JMA
   - BLACK은 화이트리스트로 못 찾으면 2차 출처를 쓸 수 있되, footnote에 "(2차 출처)" 라벨 명시.

4. **Pre-Processing Pack 저장.**
   - 위 1~3 결과를 `{session_dir}/pre-processing.json`에 저장. BLACK·RGSB 모두 이 파일을 참조한다.
   - 포맷: `{"dates_resolved": {...}, "param_defaults": {...}, "primary_sources": [...]}`.

5. **BLACK 프롬프트 첨부.**
   - Phase 3 BLACK dispatch 시 Pre-Processing Pack을 다음 블록으로 user prompt 머리에 박는다:
     ```
     [PRE-PROCESSING PACK]
     dates_resolved: {...}
     param_defaults: {...} ← 산출물 표지에 명시 라벨로 반드시 노출
     primary_sources_first: [난카이 공식, JR 공식, 외교부, ...]
     [/PRE-PROCESSING PACK]
     ```

**금지 (재발 방지):**
- 상대 날짜를 BLACK에게 그대로 던지기 ("다음주 금요일부터" → BLACK이 자기 계산).
- 인원·예산 같은 결정 핵심 파라미터를 무가정 상태로 BLACK에 넘기기.
- fact-heavy 케이스에서 화이트리스트 없이 BLACK이 검색만 자율 수행.

이 절차는 매 호출마다 30~60초 추가되지만, R1 평균을 0.5점 이상 끌어올려 R2 진입 빈도가 줄어든다. 결과적으로 전체 소요 시간은 감소.

#### 2-4. Enrich Field (선택)

케이스 정의에 `enrich:` 필드가 있으면, BLACK이 작성하기 전에 외부 스킬을 호출해 컨텍스트를 보강합니다.

처리:
1. 케이스의 `enrich` 리스트 순회
2. 각 항목의 `skill` 이름으로 사용자 환경에 해당 스킬이 설치되어 있는지 확인
3. `when` 조건 평가 (Claude 자체 판정 — Python 스크립트 없음):
   - `always`: 무조건 호출
   - `company_name_detected`: xxxxx에 회사명/티커가 포함되었는지 메인 Claude가 판정
   - `strategic_question_detected`: xxxxx가 전략적 질문(경쟁/시장/조직/M&A)인지 메인 Claude가 판정
   - `design_artifact_detected`: 산출물이 디자인을 갖는 결과물(HTML 페이지·랜딩·웹사이트·슬라이드 덱·이미지·로고·브랜드 키트 등)인지 메인 Claude가 판정. taste-skill enrich에 사용.
4. 조건 통과 시 Claude가 `Skill` 도구로 `{skill}` 스킬을 호출하거나 (스킬이 사용자 환경에 등록된 경우), 미설치 시 조용히 건너뛴다. enrichment 결과는 Phase 3 BLACK 프롬프트에 그대로 텍스트로 첨부.
5. 결과를 `enrichments[skill_name]`에 저장
6. Phase 3 BLACK draft에서 user prompt에 다음 형식으로 첨부:
   ```
   [ENRICHMENT FROM /{skill}]
   {result_summary}
   [/ENRICHMENT]
   ```

폴백:
- 스킬 미설치 → 조용히 건너뜀, 일반 모드로 진행
- `when` 미통과 → 호출 안 함
- 호출 실패 → 경고 로그, 일반 모드로 진행

### Phase 3 — BLACK DRAFT (Producer)

목적: 케이스 BLACK 페르소나 캐스팅으로 산출물 1차 작성.

메인 Claude가 `Agent` 도구로 BLACK 서브에이전트(`agents/roasting-black.md`) 호출. 입력: xxxxx + 케이스 정의 + 슬라이드 템플릿 (`html_mode`가 `slides`·`landing`·`assisted`일 때만 — `direct` 모드는 템플릿 없이 BLACK이 단일 HTML 직접 작성) + 이전 라운드 코멘트 (Round 2+) + enrichments (Phase 2-4에서 수집된 경우) + **Pre-Processing Pack** (Phase 2-3 결과 — 날짜 환산·파라미터 기본값·1차 출처 화이트리스트) + (generic_case일 때) generic 페르소나 프로파일 + **fact-heavy 도메인 신호 감지 시 fact-grounding 활성화 지시**. 출력: `{session_dir}/round-{n}/black-draft.{md|html}` (session_dir은 Phase 0에서 결정).

**fact-grounding 활성화 신호:** 입력에 여행·식당·명소·회사·재무·통계·뉴스·인물·가격·사양 같은 사실 정보가 포함되면 BLACK 프롬프트에 "fact-heavy 모드"로 라벨링. BLACK은 WebSearch/WebFetch로 1차 출처를 확보한 뒤 인라인 링크·footnote 형태로 출처를 산출물에 박는다. 상세 규약은 `agents/roasting-black.md`의 "Fact-Grounding 규약" 절. 출처 없이는 구체값 작성 금지.

**이미지 활성화 신호:** HTML 산출물(`html_mode` = slides·landing·direct·assisted) 또는 Markdown 산출물에서 시각 자료가 본문 흐름에 자연스러운 케이스(여행·브랜드·회사 분석 등)는 BLACK이 이미지를 포함. 사용자 제공 → 공식 출처 → 무료 스톡 → 명시적 자리표시자(`<div class="img-placeholder">`) 순. 가짜 URL 금지. 상세는 `agents/roasting-black.md`의 "이미지 규약" 절.

상세 호출 의사코드는 `references/orchestration.md` 참조.

산출물 저장 후 Phase 4로.

### Phase 4 — ANTI-PATTERN CHECK (Self-correction loop)

목적: BLACK 산출물의 9종 안티패턴 검출 → 발견 시 BLACK 재작성 (라운드 카운트 안 깎임). 3-strikes 보호.

**검출 룰 9종:** `hallucinated-number` · `legal-risk-term` · `missing-gold-hook` · `tone-mismatch` · `vague-cta` · `unsourced-fact` · `fake-image-url` · `internal-contradiction` · `slide-template-violation`. 각 룰의 `applies_to_categories`로 케이스 카테고리별 적용 여부 결정.

**`internal-contradiction` 룰:** BLACK 산출물 내부의 자기 모순 검출.

**`slide-template-violation` 룰:** HTML 슬라이드 산출물에서 진짜 베이스 룰 위반 검출. 사용자 화면에서 깨지는 사고를 차단. 검출 조건:
- `<deck-stage>` 태그 사용 (환각 룰, 0회여야 함)
- `deck-stage.js` 스크립트 로드 (404 파일, 0회여야 함)
- `width: 1920px` 또는 `height: 1080px` 고정 픽셀 사용 (0회여야 함)
- `<div class="deck">` 컨테이너 1회 누락
- `aspect-ratio: 16 / 10` 누락
- `container-type: inline-size` 누락
- `cqi` 단위 사용량 10회 미만 (실제로는 50회 이상이 정상)
- 슬라이드 케이스인데 `<script` 태그 사용 (JS 0줄이 진짜 룰)

**Phase 4 강화 — BLACK Self-Check + 메인 grep 교차 검증 의무화:**
BLACK Self-Check 4축 통과 보고가 실제 grep 검증에서 위반 다수 발견되는 사례가 누적된다. 메인 Claude는 BLACK 산출물 받은 직후 다음 grep 패턴을 직접 실행해 거짓 통과를 차단:
- em dash 0회 (`grep -c "—"`)
- 환각 룰 0회 (`grep -c "<deck-stage>\|deck-stage.js\|1920px\|1080px"`)
- 진짜 베이스 룰 존재 (`grep -c "class=\"deck\"\|aspect-ratio: 16 / 10\|container-type: inline-size\|cqi"`)
- 카테고리별 추가 패턴

각 룰의 `applies_to_categories`로 케이스 카테고리별 적용 여부 결정.

처리 (Claude 절차 — Python 스크립트 없음. 메인 Claude가 직접 수행):

1. 안티패턴 검출. 메인 Claude가 `references/anti-patterns/*.md` 중 케이스 카테고리에 적용된 항목만 로드한 뒤, BLACK 산출물 전문을 읽고 패턴별 양성 여부를 판정한다.
   - 참고용 의사코드 (Claude가 동일하게 수행):
     ```python
     detected = detect_all(
         black_output=draft_text,
         case_id=case.id,
         case_category=case.category,
         case_black_tone=case.black_tone,
         case_gold_scenario=case.gold_scenario,
         user_xxxxx=xxxxx,
     )
     ```
2. detected가 비어있으면 → Phase 5로.
3. 검출된 각 안티패턴마다 strike 카운터를 1 증가. `{session_dir}/strikes.json`에 누적 기록. 동일 패턴이 연속 3회 검출되면 (3-strikes) → 사용자 보고:
     ```
     [{pattern_name}] 안티패턴이 3회 연속 검출되었습니다.
     해소가 어렵습니다. 어떻게 할까요?
     (1) 진행 (강제 통과)
     (2) 중단
     (3) 케이스 재선택
     ```
4. 3-strikes 미달 시 → BLACK 재호출, prompt에 재작성 지시 추가:
   ```
   직전 산출물에서 다음 안티패턴이 검출되었습니다:
   - {ap.name}: {ap.detail}
   
   재작성하세요. 라운드 카운트는 변동 없습니다.
   ```
5. 수정된 산출물로 다시 Phase 4 → 통과 시 Phase 5.

`anti-patterns.json` 저장: `{detected_iterations: [[...], [...]], final: []}`

### Phase 5 — RGSB REVIEW (4인 병렬 채점)

목적: BLACK 산출물을 RED·SILVER·BLUE·GOLD 4인이 병렬 채점, 평균 ≥ 9.5 게이트.

**경로 자동 선택:** `TeamCreate` 도구가 가용하면 **Agent Teams 경로** (토론 가능), 아니면 **Sub-Agent 폴백** (병렬 채점만, 토론 불가).

상세 의사코드는 `references/orchestration.md` 참조.

#### 5.1 Round 1 진입

**Agent Teams 경로** (Primary):
```
TeamCreate("5color-rgsb-{case_id}-{session_id}", members=[RED·GOLD opus, SILVER·BLUE sonnet])
SendMessage(to="all", content={black_draft, case_definition, round})
```

**Sub-Agent 폴백** (TeamCreate `NotAvailable`/`Forbidden` 시):
```
for reviewer in [RED, GOLD, SILVER, BLUE]:
    Agent(subagent_type="general-purpose", run_in_background=True,
          prompt=f"agents/roasting-{reviewer}.md + 케이스 페르소나 + BLACK 산출물 → 1-10 점수 JSON")
```

#### 5.2 채점 + σ 토론

각 페르소나는 `{score, reason, suggestion}` JSON 반환 → `TaskCreate("scoring-table-round-{n}")`.

메인이 σ 계산:
- **σ < 0.5**: 합의 강함, 평균 사용
- **σ ≥ 0.5 (Agent Teams)**: 1라운드 토론 — 가장 높은 ↔ 가장 낮은 페르소나가 `SendMessage`로 코멘트 교환 후 재채점. 동률 시 타이브레이커 `GOLD > RED > SILVER > BLUE`. 1라운드 후도 σ ≥ 0.5면 "합의 실패" 표시.
- **σ ≥ 0.5 (Sub-Agent)**: 토론 불가, 분포 그대로 표시 + 사용자 알림.

#### 5.3 게이트

평균 ≥ 9.5 → Phase 7. 미만 → Phase 6 (round +1).

#### 5.4 라이프사이클 (★ 케이스당 1팀)

| | Round 1 | Round n+1 | Phase 7 직전 |
|---|---|---|---|
| Agent Teams | TeamCreate | (재사용) | TeamDelete |
| Sub-Agent | 신규 dispatch | 신규 dispatch | (없음) |

라운드 간 RGSB 컨텍스트 유지로 일관성 ↑. 4라운드 cap이 드리프트 자연 해소.

### Phase 6 — LOOP (조건부 backedge)

| 조건 | 행동 |
|---|---|
| 평균 ≥ 9.5 | Phase 7 |
| < 9.5 + round_count < 4 | round_count += 1; BLACK 재호출 (RGSB 코멘트 + 이전 산출물) → Phase 3 |
| < 9.5 + round_count == 4 | 강제 종료. 가장 높았던 라운드 결과 사용. 사용자 보고 "9.5 미달 (max=X.Y). 캐스팅 또는 과제 정의 문제 가능성. 1on1 권장" |

#### 6.1 RGSB 코멘트 Trust 룰

BLACK이 RGSB 코멘트를 받았을 때, 모든 코멘트를 무비판적으로 반영하면 명백한 사실 오류 코멘트(예: 페르소나가 요일·날짜·고유명사를 잘못 판정)까지 산출물에 박혀 품질이 오히려 떨어진다. 그렇다고 BLACK이 코멘트를 임의로 무시하면 RGSB 채점 체계가 무력화된다. 명시적 trust 룰을 둔다.

**기각 가능 조건 (BLACK이 사유 명시 후 코멘트 무시):**
- Pre-Processing Pack의 `dates_resolved`·`param_defaults`와 명백히 충돌하는 페르소나 코멘트 (예: Pack에 "5/22 (Fri)" 박혀 있는데 RED가 "5/22는 토요일" 주장).
- 1차 출처(Pre-Processing Pack의 `primary_sources_first` 또는 BLACK이 footnote로 박은 출처)와 명백히 충돌하는 코멘트.
- 케이스 정의의 BLACK 페르소나 톤·분량 제약과 정반대 방향을 강요하는 코멘트.

**기각 절차 (강제):**
1. 코멘트 기각 시 BLACK은 `{session_dir}/round-{n}/rejected-comments.md`에 다음 형식으로 사유 명시:
   ```
   ## Round {n} 기각 코멘트
   - 페르소나: RED
   - 코멘트 요지: "5/22를 토요일로 봐야 한다"
   - 기각 사유: Pre-Processing Pack dates_resolved="2026-05-22 (Fri)"과 충돌. 2026-05-17(일) + 5일 = 금요일이 정합.
   - 출처: pre-processing.json
   ```
2. 기각 사유는 Phase 7의 `reasoning.md`에 그대로 copy되어 산출물 결정 로그에 남는다.
3. 한 라운드에 같은 페르소나의 코멘트를 2개 이상 기각하면 사용자 알림: "{persona} 코멘트 2건 이상 기각. 페르소나 캐스팅 재검토 필요할 수 있습니다." (1턴 confirm).

**기각 금지 (필수 반영):**
- 페르소나의 도메인 디테일·시나리오 빈칸·매거진 톤 비평.
- 출처와 충돌하지 않는 모든 사실 보강 권고.
- 안티패턴 검출과 같은 방향의 코멘트.

이 룰은 BLACK이 페르소나 의견을 평가할 때 "출처·Pack·페르소나 정의"라는 세 축에 한해 자율 판단을 허용하고, 그 외는 모두 반영 의무. 결과적으로 페르소나가 흔들려도 BLACK이 중심을 잡는다.

### Phase 6.5 — KOREAN POLISH PASS (한국어 검증 의무 패스)

**핵심 원칙: Phase 6 게이트 통과 직후, Phase 7 출력 직전에 산출물의 한국어가 사람 글로 읽히는지 검증한다.** /roasting의 RGSB는 콘텐츠 품질을, 본 패스는 한국어 자연스러움을 본다. 두 레이어가 독립적으로 돈다.

상세 절차·페르소나 시스템 프롬프트·10패턴 정량 룰은 [`references/korean-polish.md`](references/korean-polish.md) 참조.

#### 트리거 조건

다음 중 하나라도 만족하면 본 패스 실행:
- 산출물에 한국어 본문(Markdown 또는 HTML 안의 텍스트)이 200자 이상 포함됨
- 케이스가 외부 커뮤니케이션·소셜미디어·내부 커뮤니케이션·분석 보고서·의사결정 전략·마케팅·커리어 카테고리

산출물이 한국어가 거의 없는 경우(예: 영문 이미지 프롬프트, 코드, 숫자 표) → 스킵.

#### 두 가지 실행 모드

**간소 모드 (기본, 자동):** 메인 Claude가 직접 10패턴 grep + 6항 자체검증 + AI 티 점수 산출. 1~2분 추가.

1. 본문 텍스트 추출 (HTML이면 `<style>`·`<script>`·CSS 토큰 제외)
2. 10패턴 grep 카운트 (L3·L2·L1 분류)
3. AI 티 점수 산출: `점수 = 10 − (L3 × 2.0) − (L2 × 0.5) − (L1 × 0.2)`
4. 등급 판정:
   - **A**: 점수 ≥ 9.0, L3 = 0 → 사람 글로 통과 ✅
   - **B**: 점수 8.0~8.9, L3 = 0, L2 ≤ 4 → 합격 ✅
   - **C**: L3 1~2개 또는 점수 7.0~7.9 → 사용자 컨펌 (정밀 모드 권고)
   - **D**: L3 ≥ 3개 또는 점수 < 7.0 → 사용자 컨펌 (사람 검수 권고)
5. 6항 자체검증 (의미 동등·변경률·말투·장르·등급·em dash)
6. 결과를 `final/korean-polish.md`에 별도 파일로 보고

**정밀 모드 (옵션):** 사용자가 명시 요청 또는 간소 모드 등급 C·D 컨펌 시 진입. BLACK polish 페르소나 + RGSB 4인 풀 패스. 5~10분 추가. 페르소나 평균 9.7 + GOLD 체류도 9.7 + AI 티 등급 A 모두 만족 시 통과.

#### 산출물 자동 수정 금지

본 패스가 자동으로 BLACK을 재호출해 산출물을 수정하지 않는다. 사용자가 명시적으로 정밀 모드를 요청해야 한다. 등급 A·B면 산출물 그대로 Phase 7로, C·D면 사용자 컨펌 후 처리.

#### Phase 7 산출물 영향

- 등급 A·B → 산출물 그대로 출력, `final/korean-polish.md` 첨부
- 등급 C·D → 사용자 컨펌 후 결정 (그대로 출력 / 정밀 모드 / 사람 검수)

### Phase 7 — DELIVER (4종 출력)

처리 (Claude 절차 — Python 스크립트 없음. 메인 Claude가 직접 파일 출력):

1. `TeamDelete` (Agent Teams 경로일 때만).
2. `{session_dir}/final/` 디렉토리 생성 (session_dir은 Phase 0에서 결정 — config의 `output_dir` 또는 디폴트 `~/.claude/roasting/_workspace/`).
3. **4종 산출물 생성:**
   - `output.{html|md}`: 최종 BLACK 산출물 (출력 포맷에 따라).
   - `critique.md`: 라운드별 RGSB 4인 코멘트 정리 (교재).
   - `reasoning.md`: BLACK 결정 로그 + 안티패턴 검출 이력 + 라운드 진화.
   - `korean-polish.md`: Phase 6.5 한국어 검증 결과 (등급·AI 티 점수·10패턴 카운트·6항 자체검증). 한국어 본문 200자 미만 케이스는 생략.
4. **표준 완료 푸터 (모든 호출에 강제):**

   ```
   ✅ 완료 — 20260517_01

   - 소요 시간: 8분 31초 (13:37:00 → 13:45:31)
   - 주요 업무: c41 임원 PPT · 2라운드 · 평균 9.625 ✅
   - 카카오톡: 📱 발송됨

   산출물 위치: ~/Desktop/Roasting/20260517_01/final/
   - 20260517_01/final/output.html     ← 임원이 사용
   - 20260517_01/final/critique.md     ← RGSB 4인 평가 (교재)
   - 20260517_01/final/reasoning.md    ← BLACK 결정 로그

   다음 액션:
   1) 산출물 보기
   2) critique 보기
   3) 다시 호출 (/roasting xxxxx)
   4) 피드백 (/roasting --feedback)
   ```

   **세 가지 메타 항목은 절대 빠뜨리지 않는다 — 소요 시간 / 주요 업무 한 줄 / 카카오톡 발송 여부.**
   - 소요 시간: `{session_dir}/meta.json`의 `started_at`과 현재 시각의 차. `N분 M초` 포맷.
   - 주요 업무: `{case_id} · {라운드}라운드 · 평균 {score}` 한 줄. generic_case면 case_id 자리에 `generic_case`로 표기.
   - 카카오톡: `mcp__*__KakaotalkChat-MemoChat` 도구가 사용자 환경에 등록되어 있으면 자동 호출, 미설치/미연결 시 "스킵"으로 표시. 메시지 본문은 위 3줄을 압축한 200자 이내(스킬 호출 결과 / 케이스 / 라운드 / 점수 / 소요 시간 / 경로).

   **경로 안내 형식:** 산출물 위치와 파일 경로는 항상 `{output_dir}/{YYYYMMDD}_{NN}/final/output.{html|md}` 같이 **세션 ID 폴더명을 포함한 전체 경로**로 보여준다. 예: `~/Desktop/Roasting/20260517_01/final/output.html`. session_id를 노출해야 사용자가 그날 N번째 작업물을 즉시 식별할 수 있다.
5. **익명 telemetry 전송 (옵트인 시 — 현재 비활성, GA에 활성화 예정):**
   - 참고용 의사코드 (실제 호출은 GA에 추가, 콘텐츠 텍스트는 절대 포함 안 됨):
   ```python
   if config.telemetry_enabled:
       telemetry.send({
           "user_id": user_uuid,
           "skill_version": _read_version(),  # plugin.json에서 동적 로드
           "case_id": case.id,
           "final_score": avg_score,
           "round_count": rounds,
           "slide_template_id": slide.id if slide else None,
           "total_cost_usd": cost,
           "anti_patterns_detected": ap_counter.counts,
           "debate_triggered": any_debate,
           "completion_status": "passed" | "forced" | "user_aborted",
       })
   ```
   콘텐츠 텍스트는 절대 포함 안 됨. `_read_version()`은 `.claude-plugin/plugin.json`의 `version` 필드를 읽음 (하드코딩 금지).

## 컨펌 시점

| 시점 | Phase | 트리거 | 디폴트 | 부담 |
|---|---|---|---|---|
| 라우팅 | 1 | 신뢰도 < 0.85 | top-1 자동 | 1턴 |
| 슬라이드 | 2 | `slides`·`landing`·`assisted` 모드 첫 호출 (preferences에 미저장 시) | top-1 추천 | 1턴 (저장) |
| 안티패턴 무한 루프 | 4 | 동일 안티패턴 3회 | 사용자 선택 | 1턴 (예외) |
| 토론 합의 실패 | 5 | 1라운드 후 σ ≥ 0.5 | 분포 그대로 | 0 |
| 4라운드 미통과 | 6 | round=4 + score < 9.5 | 강제 출력 + 사유 | 0 |

## 에러 폴백

| 에러 | 폴백 |
|---|---|
| `TeamCreate` 사용 불가 | Sub-Agent 경로 (Phase 5.1 참조) |
| Opus 일시 불가 | RED/GOLD를 Sonnet으로 자동 다운그레이드 + 사용자 알림 |
| 라우팅 모든 후보 신뢰도 < 0.5 | generic 5-Color 모드 (Phase 1 §5 참조 — BLACK+RGSB 워크플로우는 단축 없이 그대로 실행, 페르소나만 generic 프로파일) |
| 슬라이드 템플릿 fetch 실패 | Markdown 폴백 + 경고 footer |
| `{session_dir}` 부모 폴더 디스크 풀 | 가장 오래된 세션 5개 자동 삭제 + 재시도. config의 `output_dir`이 사용자 폴더(예: Desktop)면 삭제 대신 사용자에게 알림 후 중단. |
| enrich 스킬 미설치 | 조용히 건너뜀, 일반 모드로 진행 |
| 영어 입력 (한국어 전용 스킬) | generic 5-Color (Phase 1 §5와 동일 절차). 사용자에게 한국어 요청 권유 |

## 사용 예시

| 입력 | 라우팅 결과 | 출력 |
|---|---|---|
| `/roasting 거래처 부장한테 8월 12일까지 회신 달라는 메일` | c1 외부 비즈니스 이메일 | `output.md` 200-500자 + `critique.md` |
| `이번 분기 임원 PPT 만들어줘` | c41 임원용 PPT | `output.html` (slide_library `slides` 모드) |
| `B2B SaaS 랜딩페이지 만들어줘` | c70 웹사이트·랜딩페이지 | `output.html` (slide_library `landing` 모드, 한 페이지) |
| `Stripe 스타일 SaaS 웹사이트 한 페이지 만들어줘` | c73 웹사이트 제작 | `output.html` (`direct` 모드, BLACK이 단일 HTML 직접 작성) |
| `인스타 릴스 커버 이미지 프롬프트 짜줘` | c74 이미지 제작 | `output.md` 7단 프롬프트 세트 (장면·구도·조명·색감·스타일·비율·네거티브) |
| `삼성전자 분기 실적 1페이지로 정리해줘` | c75 DART 기반 회사 분석 (`/dart` enrich) | `output.md` IR 메모 |
| `신사업 검토할 때 어떤 프레임워크 써야 할까` | c76 전략 프레임워크 메모 (`/strategy` enrich) | `output.md` 1프레임워크 결정 메모 |
| `5월 조직개편 사내 공지 다듬어줘` | c16 사내 공지 | `output.md` |
| `LP 분기 레터 써줘` | c35 LP 리포트 | `output.md` |
| `공급사 사과문 검토해줘` | c2 사과문 (LEGAL_RISK_TERM 안티패턴 적용) | `output.md` + 단정 약속어 자동 검출 |

각 출력에는 항상 4종 산출물이 함께 저장됩니다: `output.{md|html}` (산출물) · `critique.md` (RGSB 4인 평가, 교재) · `reasoning.md` (BLACK 결정 로그) · `korean-polish.md` (한국어 검증 결과, 한국어 200자 미만이면 생략).

## 참조 파일 인덱스

| 경로 | 내용 | 로드 시점 |
|---|---|---|
| `references/cases/_index.md` | 68 케이스 1줄 라우팅 인덱스 (~30KB) | Phase 1 |
| `references/cases/p*.md` | 케이스별 BLACK + RGSB 페르소나 + GOLD 시나리오 + (선택) `enrich:` | Phase 2 (매칭 시) |
| `references/anti-patterns/*.md` | 9종 검출 룰 (`hallucinated-number`, `legal-risk-term`, `missing-gold-hook`, `tone-mismatch`, `vague-cta`, `unsourced-fact`, `fake-image-url`, `internal-contradiction`, `slide-template-violation`) + BLACK 재작성 지시 | Phase 4 (적용 안티패턴만) |
| `references/slide-templates/index.json` | 35 슬라이드 템플릿 메타 (color × formality) | Phase 2 (`slides`·`landing`·`assisted` 모드 HTML 케이스) |
| `references/workflow.md` | 9.5 합격선 · 4라운드 cap · 발화 톤 · `_workspace` 컨벤션 | 워크플로우 룰 참조 시 |
| `references/output-formats.md` | 카테고리별 출력 포맷 (PPT=HTML, 외=Markdown) | Phase 7 (산출물 정리) |
| `references/orchestration.md` | Phase 3·5 의사코드 상세 (Agent Teams + Sub-Agent 분기) | Phase 5 구현 참조 시 |
| `references/korean-polish.md` | Phase 6.5 한국어 검증 절차 + 10패턴 정량 룰 + 정밀 모드 페르소나 시스템 프롬프트 | Phase 6.5 진입 시 |
| `agents/roasting-{black,red,silver,blue,gold}.md` | 5인 페르소나 *공통* 행동 규약 + 팀 통신 프로토콜 | Phase 3·5 호출 시 system prompt |

## 검증된 품질 지표 (베타 측정값, 후속 패치에서 회귀 없음)

| 게이트 | 목표 | 실측 | 출처 |
|---|---|---|---|
| 라우팅 정확도 (top-1) | ≥ 90% (Wilson 95% LB) | **98.4%** (LB 0.954) | `tests/routing/test_routing_accuracy.py` (195 phrasings × Haiku judge) |
| 안티패턴 false positive | 0% | **0%** (50/50) | `tests/anti_patterns/` (5종 × 양성 5 + 음성 5) |
| 단위/통합 테스트 | green | **97/97 pass** | `pytest -m "not slow and not network"` |
| 품질 게이트 시나리오 평균 | ≥ 9.0 | **9.17** (1/15 실측) | `tests/quality/test_quality_gate.py` |

베타 사용자 데이터로 GA 게이트(평균 ≥ 9.5, 50명 + 100 피드백) 자연 검증.

## Ecosystem (인접 스킬 통합)

`enrich:` 필드로 다른 Claude Code 스킬을 호출해 컨텍스트 보강. 현재 declared:

| 케이스 / 모드 | enrich 스킬 | when |
|---|---|---|
| c25 기획안·제안서, c45 컨설팅 덱, c37 산업·시장 분석, c40 경영 진단, c76 전략 메모 | `/strategy` | strategic_question_detected |
| c28 이사회 보고서, c29 주주 서한, c33 분기 실적 리뷰, c75 DART 회사 분석 | `/dart` | company_name_detected |
| c31 IR 발표 | `/dart` | always |
| c34 IC Memo | `/dart` + `/strategy` | dart=company_name_detected, strategy=always |
| **c70 랜딩페이지, c73 웹사이트 제작, c41/42/43/45 PPT, `assisted` 모드** | **`/design-taste-frontend`** | **always (HTML 산출물)** |
| **c70 랜딩페이지** (추가) | **`/high-end-visual-design`** | **always (프리미엄 톤 보강)** |
| **c74 이미지 제작** | **`/imagegen-frontend-web` 또는 `/brandkit`** | **always (이미지 유형에 따라 자동 선택)** |
| **c59 브랜드 가이드** | **`/brandkit`** | **always** |

**현재 상태:** enrich 호출은 메인 Claude가 `Skill` 도구로 직접 dispatch (별도 Python 스크립트 없음). 사용자 환경에 해당 스킬이 등록되지 않았으면 조용히 건너뛰고 BLACK이 자체 판단으로 진행 (graceful degradation).

설치 가이드: `/dart`, `/strategy`는 별도 설치. taste-skill 계열(`/design-taste-frontend`, `/high-end-visual-design`, `/imagegen-frontend-web`, `/brandkit` 등)은 한 번에 설치:

```bash
npx skills add https://github.com/Leonxlnx/taste-skill
```

또는 특정 변형만:

```bash
npx skills add https://github.com/Leonxlnx/taste-skill --skill "design-taste-frontend"
```

## Design Taste Integration (taste-skill 통합)

디자인을 갖는 산출물(HTML 페이지·웹사이트·랜딩·슬라이드 덱·이미지 프롬프트·브랜드 키트·로고 등)은 [taste-skill](https://github.com/Leonxlnx/taste-skill) 외부 스킬 계열을 자동 enrich해 anti-slop 가이드라인을 BLACK 프롬프트에 주입한다. taste-skill은 generic AI 출력 특유의 "지루하고 평범한" 디자인을 막고 레이아웃·타이포·여백·모션 품질을 끌어올리는 프레임워크다.

### 변형 매핑

| 산출물 유형 | 1순위 변형 | 2순위 (선택) |
|---|---|---|
| HTML 페이지 일반 (assisted·landing·direct·slides 모두) | `design-taste-frontend` | — |
| 프리미엄·고급 톤 랜딩 (c70 등) | `design-taste-frontend` | `high-end-visual-design` |
| 미니멀·에디토리얼 톤 (Notion/Linear 풍 요청) | `minimalist-ui` | `design-taste-frontend` |
| 브루털리스트·실험적 톤 요청 | `industrial-brutalist-ui` | — |
| 이미지 — 웹 컴프·히어로 시각 (c74 일부) | `imagegen-frontend-web` | — |
| 이미지 — 모바일 화면·플로우 | `imagegen-frontend-mobile` | — |
| 이미지 — 로고·팔레트·아이덴티티·브랜드 보드 (c74 일부, c59 전체) | `brandkit` | — |
| 잘려서 끝나는 긴 HTML 출력이 반복될 때 | `full-output-enforcement` | — |

### 동작

1. Phase 2 SEED LOAD 직후, 케이스 frontmatter의 `enrich` 블록 또는 generic_case + HTML 신호가 있으면 → 메인 Claude가 변형 1순위를 자동 선택해 `Skill` 도구로 호출.
2. taste-skill이 제공하는 디자인 가이드라인을 받아 Phase 3 BLACK 프롬프트에 다음 형식으로 첨부:
   ```
   [ENRICHMENT FROM /design-taste-frontend]
   {anti-slop 가이드라인 텍스트}
   [/ENRICHMENT]
   ```
3. BLACK은 케이스 BLACK 페르소나(예: c73의 Stripe·Linear·Vercel 톤) + taste-skill 가이드라인을 모두 흡수해 산출.
4. 미설치 시 조용히 스킵, BLACK이 케이스 페르소나만으로 진행 + 사용자에게 1회 안내:
   > 디자인 품질을 더 끌어올리려면 `npx skills add https://github.com/Leonxlnx/taste-skill` 설치를 권장합니다. 현재는 케이스 페르소나만으로 진행합니다.

### 변형 자동 선택 로직 (Claude 절차)

메인 Claude가 입력 + 케이스 정보를 보고 1순위 변형을 고른다:

- 입력에 "미니멀·심플·깔끔·Notion·Linear" → `minimalist-ui`
- 입력에 "고급·프리미엄·럭셔리·calm·spacious" 또는 c70 → `design-taste-frontend` + `high-end-visual-design`
- 입력에 "Stripe·Vercel·Linear" 또는 c73 → `design-taste-frontend`
- 입력에 "브루털·실험적·industrial" → `industrial-brutalist-ui`
- 입력에 "이미지·사진·시각·hero shot·landing visual" + 모바일 신호 없음 → `imagegen-frontend-web`
- 입력에 "이미지" + "iOS·Android·앱·모바일" → `imagegen-frontend-mobile`
- 입력에 "로고·브랜드·아이덴티티·팔레트·typography 키트" 또는 c59 → `brandkit`
- 그 외 HTML 산출물 → `design-taste-frontend` (기본)

## 한 줄 요약

`/roasting xxxxx` (또는 자연어) → 68 케이스 자동 라우팅 → BLACK 1명 + RGSB 4인 5-Color → 9.5 합격선 + 4라운드 → 산출물 3종.

**한국어 전용. 베타.** 세부 변경 이력은 [`CHANGELOG.md`](../../CHANGELOG.md) 참조.
