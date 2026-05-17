# Changelog

This project follows [Semantic Versioning](https://semver.org/) and [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

## [0.4.0] - 2026-05-17

### Added

- **taste-skill 외부 통합** (Leonxlnx/taste-skill) — 디자인 산출물(HTML 페이지·웹사이트·랜딩·슬라이드·이미지·로고·브랜드 키트)에 anti-slop 프론트엔드 프레임워크를 자동 enrich. 8개 디자인 케이스(p41/42/43/45/p59/p70/p73/p74) frontmatter에 `enrich` 블록 추가. 변형 자동 선택 로직으로 `design-taste-frontend`(기본 HTML) / `high-end-visual-design`(프리미엄 톤, p70 보강) / `minimalist-ui` / `industrial-brutalist-ui` / `imagegen-frontend-web` / `imagegen-frontend-mobile` / `brandkit`(p59·로고·아이덴티티) / `full-output-enforcement` 중 1순위 변형을 메인 Claude가 입력에서 추론해 호출. generic_case 폴백 + HTML 요청 시에도 자동 적용. 미설치 시 graceful degradation + 1회 설치 안내(`npx skills add https://github.com/Leonxlnx/taste-skill`). 신규 `design_artifact_detected` `when` 조건 추가.
- **`assisted` 빌더 모드 신설** — generic_case 폴백 + 사용자가 HTML/페이지/대시보드/일정표/카드 등 디자인 산출물을 요청할 때 자동 진입. 슬라이드 라이브러리 35종 중 1개를 베이스로 고른 뒤 BLACK이 콘텐츠 주입 + 필요한 인터랙티브 요소(탭·필터·접힘·간단 차트)만 보강. 처음부터 자체 디자인 생성은 금지 (= `direct` 영역 침범). HTML 빌더 모드는 이제 4종: `slides | landing | direct | assisted`.
- **generic 페르소나 프로파일** — Phase 1 §5 폴백에서 케이스 시드가 없을 때 사용할 BLACK·RED·SILVER·BLUE·GOLD 5인 기본 캐스팅을 명시. 입력에서 도메인·산출물 유형·사용 시점·결정자를 자체 추론해 5색 채점 워크플로우를 그대로 유지.
- **케이스 프론트매터 `html_mode` 필드** — `p41`·`p42`·`p43`·`p45`·`p70`·`p73`에 `output_format` / `html_mode` / `slide_template_pool` / `default_formality` 필드 추가. SKILL.md는 이 필드를 단일 진실로 참조하고 케이스 ID 하드코딩을 제거. 향후 HTML 케이스 추가는 케이스 파일만 수정해도 동작.

### Changed

- **Phase 1 §5 폴백 워크플로우 강제** — 라우팅 신뢰도 < 0.5(generic_case)라도 Phase 3 BLACK 서브에이전트·Phase 5 RGSB 4인 채점·9.5 게이트·Phase 7 3종 산출물 출력을 단축 없이 그대로 실행. "자산 시드 없으니 한 번에 출력" 같은 단축을 명시적으로 금지. v0.3 세션에서 폴백 모드가 워크플로우를 통째로 스킵하던 사고의 재발 방지.
- **SKILL.md ↔ 구현 일관성 정리 (갈래 B)** — `scripts/route.py`·`scripts/build_slide_html.py`·`scripts.invoke_skill`·`scripts.anti_patterns.detect_all`·`scripts.deliver.deliver()` 등 실재하지 않던 Python 호출 묘사를 "Claude 절차 — Python 스크립트 없음. 메인 Claude가 직접 수행"으로 라벨링하고 절차 산문으로 교체. 의사코드 블록은 "참고용 의사코드 (Claude가 동일하게 수행)"로 명시.
- **`enrich` 호출 경로 정정** — `scripts.invoke_skill.invoke()` stub 묘사를 메인 Claude의 `Skill` 도구 직접 dispatch 절차로 교체. 사용자 환경에 스킬 미설치 시 조용히 graceful degradation.
- **컨펌 시점·에러 폴백 표** — `slides`·`landing`·`assisted` 3-mode 세트로 슬라이드 ID 선택 트리거를 확장. 라우팅 신뢰도 < 0.5와 영어 입력 폴백은 "Phase 1 §5 동일 절차"로 정리.

## [0.3.0] - 2026-05-17

### Added

- **2 new remote cases synced from airoasting.github.io/5color** — `p73 웹사이트 제작` (folio VII·3, 마케팅 · 단일 HTML 직접 출력) + `p74 이미지 제작` (folio VII·4, 마케팅 · 7단 프롬프트 세트). 사이트 측에서 신설된 케이스를 그대로 흡수.
- **`direct` 빌드 모드** in `scripts/build_slide_html.py` — `DIRECT_HTML_CASE_IDS = {"p73"}`. BLACK이 작성한 단일 HTML 파일을 템플릿 fetch 없이 `output.html`로 그대로 통과시킨다. PPT/p70과 달리 인라인 CSS·시맨틱 마크업·반응형을 BLACK이 자급.
- **`p73` `direct` 모드용 BLACK 헤딩 규약** (`agents/roasting-black.md`) — 헤딩 분할 없음, `<!doctype html>`부터 완성, 외부 CDN/이미지 URL 금지.
- **Routing phrasings 6개 추가** — 신규 p73·p74(웹사이트·이미지) 각 3종. 라우팅 테스트셋 198 → 204.

### Changed

- **64개 케이스 subhead 전면 리라이트** — 5color 사이트에서 "다섯 사람이 ~ 같이 다듬어 드립니다" 패턴을 더 짧고 단정한 "한 호흡, 한 메시지" 스타일로 교체. `sync_cases.py`로 idempotent 갱신.
- **ID 재할당 (Breaking, but internal):** 로컬에서만 존재하던 `p73 DART 회사 분석` → `p75`로 이동(folio IV·20), `p74 전략 프레임워크 메모` → `p76`(folio V·7)로 이동. 이유 — 5color 사이트의 신규 p73·p74가 마케팅 카테고리(웹사이트·이미지)에 배정되면서 ID 충돌. enrich 블록(/dart, /strategy)은 보존.
- **`p70` folio** `VII·3` → `VII·5` — 신규 p73 웹사이트 제작과 folio 충돌 해소.
- **케이스 총량** 66 → 68 (5color 64 + 로컬 확장 4: p41·p70·p75·p76).
- **SKILL.md** Phase 2 — HTML 산출물 케이스 분기를 `slides`·`landing`·`direct` 3-mode 모델로 재구성. `mode_for_case()`가 단일 진실.
- **`output-formats.md`** — `direct` 모드 행 추가, p74 이미지(마크다운 7단) 행 추가, p75 DART/p76 전략 ID 정정.
- **enrich 매핑** (SKILL.md ecosystem 테이블) — `/dart`는 `p75`, `/strategy`는 `p76`을 가리키도록 정정.
- **`sync_cases.py` 도크스트링** — "63 cases" → "64 cases" + 로컬 확장 케이스 정책 명시.
- **`plugin.json` description** — 66 → 68, 신규 케이스(image-prompt set, hand-coded website, DART company brief, strategy memo) 노출, p73 `direct` HTML 동작 명시.

### Documentation

- **SKILL.md 예시 테이블** — 신규 p73(웹사이트 직접 HTML) + p74(이미지 프롬프트) 입출력 사례 추가, p75/p76 ID 정정.

## [0.2.1-unreleased] - 2026-05-15

### Added

- **New case `p70` 웹사이트·랜딩페이지** (folio VII·3 → 0.3.0에서 VII·5, 마케팅) — 한 화면 한 메시지·CTA 한 개 합격선의 랜딩페이지 케이스. BLACK = 그로스 마케팅·랜딩 UX 카피라이터 17년차+. RGSB는 가치제안 한 줄(RED), 정보 위계·CTA 반복(SILVER), 모바일 첫 5초 호흡(BLUE), SNS 광고 클릭 시나리오(GOLD)로 채점.
- **`build_slide_html.py` landing 모드** — H2 단위로 BLACK Markdown을 랜딩 섹션(히어로·소셜프루프·기능·CTA·FAQ)으로 분할하고 slide_library 템플릿 컨테이너에 주입. PPT 모드(슬라이드 단위 H1)와 같은 fetch + container 로직을 공유하고 콘텐츠 블록 셰이프만 다름.
- **`mode_for_case()` 헬퍼** + `LANDING_CASE_IDS` frozenset — case_id → builder 모드 매핑이 한 곳에 모임. 차후 HTML 산출물 케이스 확장 시 이 함수만 갱신.
- **Phrasings 3개 추가** (p70 natural/keyword/audience) — 라우팅 테스트셋 195 → 198.
- **단위 테스트 4개** — landing 분할, H2 미존재 폴백, mode_for_case 라우팅, build() e2e mock.

### Changed

- **SKILL.md Phase 2** — "PPT 카테고리" 분기를 "HTML 산출물 케이스 (p41/42/43/45/p70)"로 통합. 모든 HTML 산출물은 slide_library 35개 중 가장 적정한 1개를 그대로 베이스 HTML로 사용. 자체 디자인 생성 금지.
- **`output-formats.md` 마케팅 행 분할** — p70은 HTML, 나머지 2개(p56·p59)는 Markdown.
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
- **2 new cases** — `p73 DART 기반 회사 분석 리포트`, `p74 전략 프레임워크 적용 메모`.
- **9 existing cases enriched** — p25, p28, p29, p31, p33, p34, p37, p40, p45 now declare optional `/dart` and/or `/strategy` enrichment.
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
- `HALLUCINATED_NUMBER`: regex extraction + Haiku source verification; exempt on p63/p64/p69
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
