---
name: roasting
description: 한국어 화이트칼라 산출물(이메일·보고서·PPT·웹사이트·이미지 프롬프트·랜딩페이지·이사회 메모·IR 자료·계약 검토·이력서·사내 공지 등 68개 케이스)을 5-Color Harness로 작성합니다. 한국 비즈니스 리더가 "써줘·다듬어줘·만들어줘·검토해줘·정리해줘" 같은 자연어 요청을 하거나 `/roasting xxxxx`로 호출하면 자동으로 케이스를 골라 BLACK 작성+RGSB 4인 채점(9.5 합격선, 4라운드)으로 산출물·평가·결정 로그를 만듭니다. PPT·랜딩페이지 케이스는 slide_library 템플릿 자동 결합, 웹사이트 제작 케이스는 단일 HTML 직접 출력. 한국어 전용. 영어 입력은 일반 모드 폴백.
---

# /roasting — 5-Color Harness Execution Engine

5color 사이트의 64개 케이스 + 4개 로컬 확장 케이스(p41 임원 PPT · p70 랜딩페이지 템플릿 결합 · p75 DART 회사 분석 · p76 전략 프레임워크 메모) = 총 68개 케이스를 Claude Code 위에서 *집행*하는 엔진. 임원이 자연어 한 줄로 호출하면, 7-Phase 워크플로우(Pipeline + Supervisor 패턴, Phase 5만 Agent Teams)로 산출물·평가·결정 로그 3종을 출력한다.

## 핵심 원칙

1. **단일 진입**: `/roasting xxxxx` 한 줄만 학습. 도메인은 자동 라우팅.
2. **Progressive Disclosure**: 케이스 1줄 인덱스만 항상 컨텍스트, 매칭 시 케이스 풀 정의 로드.
3. **5-Color 본래 의도 충실**: 4인 RGSB가 *서로 토론* (σ ≥ 0.5 자동 트리거).
4. **콘텐츠 0 수집**: telemetry는 메타데이터만. xxxxx·산출물·코멘트는 외부 전송 0.
5. **결정적 비용**: 5명 × 4라운드 cap × 케이스 정의 고정 = 호출당 ~$0.36.

## 워크플로우 (7 Phase)

### Phase 0 — 진입과 세션 초기화

트리거 시:
1. 세션 디렉토리 생성: `~/.claude/roasting/_workspace/{YYYYMMDD-HHMMSS}-{tmp_id}/`
2. `input.txt`에 xxxxx 저장
3. session_dir 경로를 모든 후속 Phase가 공유

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
   - Phase 7 3종 산출물 (`output.*` · `critique.md` · `reasoning.md`) 동일 생성.

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
   - 사용자 입력에 "이미지·사진·로고·브랜드·시각·hero shot" 같은 신호가 있으면 → 출력 포맷 `md` (7단 이미지 프롬프트 세트, p74 톤 차용).
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
   - **`assisted` 모드 (신설 v0.4):** generic_case 폴백 + 사용자가 HTML 요청 시 자동 진입. 35개 템플릿 중 1개를 골라 베이스 HTML로 사용하되, BLACK이 콘텐츠 주입 + 필요 시 인터랙티브 요소(탭·필터·접힘·간단 차트) 보강 허용. 자체 디자인 시스템 처음부터 생성 금지. 상세는 `references/output-formats.md` "assisted 모드" 절 참조.
   - `slides`·`landing`·`assisted` 모드는 슬라이드 ID 선택이 필요하다 (`~/.claude/roasting/preferences/{case_id}.json` 확인 → 존재 시 자동, 없음 시 top-3 추천 + 1턴 confirm + preferences 저장. assisted는 `generic_case` 키로 저장). `direct` 모드는 슬라이드 ID가 무의미하므로 이 단계를 건너뛴다.
3. 케이스 카테고리 따라 `references/anti-patterns/*.md` 중 적용 항목만 로드.
4. `case-context.json` 저장.

#### 2-3. Enrich Field (선택)

케이스 정의에 `enrich:` 필드가 있으면, BLACK이 작성하기 전에 외부 스킬을 호출해 컨텍스트를 보강합니다.

처리:
1. 케이스의 `enrich` 리스트 순회
2. 각 항목의 `skill` 이름으로 사용자 환경에 해당 스킬이 설치되어 있는지 확인
3. `when` 조건 평가 (Claude 자체 판정 — Python 스크립트 없음):
   - `always`: 무조건 호출
   - `company_name_detected`: xxxxx에 회사명/티커가 포함되었는지 메인 Claude가 판정
   - `strategic_question_detected`: xxxxx가 전략적 질문(경쟁/시장/조직/M&A)인지 메인 Claude가 판정
   - `design_artifact_detected`: 산출물이 디자인을 갖는 결과물(HTML 페이지·랜딩·웹사이트·슬라이드 덱·이미지·로고·브랜드 키트 등)인지 메인 Claude가 판정. taste-skill enrich에 사용.
4. 조건 통과 시 Claude가 `Skill` 도구로 `{skill}` 스킬을 호출하거나 (스킬이 사용자 환경에 등록된 경우), 미설치 시 조용히 건너뛴다. v0.4 현재 enrichment 결과는 Phase 3 BLACK 프롬프트에 그대로 텍스트로 첨부.
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

메인 Claude가 `Agent` 도구로 BLACK 서브에이전트(`agents/roasting-black.md`) 호출. 입력: xxxxx + 케이스 정의 + 슬라이드 템플릿 (`html_mode`가 `slides`·`landing`·`assisted`일 때만 — `direct` 모드는 템플릿 없이 BLACK이 단일 HTML 직접 작성) + 이전 라운드 코멘트 (Round 2+) + enrichments (Phase 2-3에서 수집된 경우) + (generic_case일 때) generic 페르소나 프로파일. 출력: `_workspace/{session}/round-{n}/black-draft.{md|html}`.

상세 호출 의사코드는 `references/orchestration.md` 참조.

산출물 저장 후 Phase 4로.

### Phase 4 — ANTI-PATTERN CHECK (Self-correction loop)

목적: BLACK 산출물의 5종 안티패턴 검출 → 발견 시 BLACK 재작성 (라운드 카운트 안 깎임). 3-strikes 보호.

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
3. 검출된 각 안티패턴마다 strike 카운터를 1 증가. `_workspace/{session}/strikes.json`에 누적 기록. 동일 패턴이 연속 3회 검출되면 (3-strikes) → 사용자 보고:
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

### Phase 7 — DELIVER (3종 출력)

처리 (Claude 절차 — Python 스크립트 없음. 메인 Claude가 직접 파일 출력):

1. `TeamDelete` (Agent Teams 경로일 때만).
2. `_workspace/{session}/final/` 디렉토리 생성.
3. **3종 산출물 생성:**
   - `output.{html|md}`: 최종 BLACK 산출물 (출력 포맷에 따라).
   - `critique.md`: 라운드별 RGSB 4인 코멘트 정리 (교재).
   - `reasoning.md`: BLACK 결정 로그 + 안티패턴 검출 이력 + 라운드 진화.
4. 사용자에게 인터랙티브 안내:
   ```
   완료. 산출물 위치: ~/.claude/roasting/_workspace/{session}/final/
   - output.{html|md}     ← 임원이 사용
   - critique.md          ← RGSB 4인 평가 (교재)
   - reasoning.md         ← BLACK 결정 로그
   
   다음 액션을 골라주세요:
   1) 산출물 보기
   2) critique 보기
   3) 다시 호출 (/roasting xxxxx)
   4) 피드백 (/roasting --feedback)
   ```
5. **익명 telemetry 전송 (옵트인 시 — v0.4 현재 비활성, v1.0 GA에 활성화):**
   - 참고용 의사코드 (실제 호출은 v1.0에 추가, 콘텐츠 텍스트는 절대 포함 안 됨):
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
| `_workspace` 디스크 풀 | 가장 오래된 세션 5개 자동 삭제 + 재시도 |
| enrich 스킬 미설치 | 조용히 건너뜀, 일반 모드로 진행 |
| 영어 입력 (한국어 전용 스킬) | generic 5-Color (Phase 1 §5와 동일 절차). 사용자에게 한국어 요청 권유 |

## 사용 예시

| 입력 | 라우팅 결과 | 출력 |
|---|---|---|
| `/roasting 거래처 부장한테 8월 12일까지 회신 달라는 메일` | p1 외부 비즈니스 이메일 | `output.md` 200-500자 + `critique.md` |
| `이번 분기 임원 PPT 만들어줘` | p41 임원용 PPT | `output.html` (slide_library `slides` 모드) |
| `B2B SaaS 랜딩페이지 만들어줘` | p70 웹사이트·랜딩페이지 | `output.html` (slide_library `landing` 모드, 한 페이지) |
| `Stripe 스타일 SaaS 웹사이트 한 페이지 만들어줘` | p73 웹사이트 제작 | `output.html` (`direct` 모드, BLACK이 단일 HTML 직접 작성) |
| `인스타 릴스 커버 이미지 프롬프트 짜줘` | p74 이미지 제작 | `output.md` 7단 프롬프트 세트 (장면·구도·조명·색감·스타일·비율·네거티브) |
| `삼성전자 분기 실적 1페이지로 정리해줘` | p75 DART 기반 회사 분석 (`/dart` enrich) | `output.md` IR 메모 |
| `신사업 검토할 때 어떤 프레임워크 써야 할까` | p76 전략 프레임워크 메모 (`/strategy` enrich) | `output.md` 1프레임워크 결정 메모 |
| `5월 조직개편 사내 공지 다듬어줘` | p16 사내 공지 | `output.md` |
| `LP 분기 레터 써줘` | p35 LP 리포트 | `output.md` |
| `공급사 사과문 검토해줘` | p2 사과문 (LEGAL_RISK_TERM 안티패턴 적용) | `output.md` + 단정 약속어 자동 검출 |

각 출력에는 항상 3종 산출물이 함께 저장됩니다: `output.{md|html}` (산출물) · `critique.md` (RGSB 4인 평가, 교재) · `reasoning.md` (BLACK 결정 로그).

## 참조 파일 인덱스

| 경로 | 내용 | 로드 시점 |
|---|---|---|
| `references/cases/_index.md` | 68 케이스 1줄 라우팅 인덱스 (~30KB) | Phase 1 |
| `references/cases/p*.md` | 케이스별 BLACK + RGSB 페르소나 + GOLD 시나리오 + (선택) `enrich:` | Phase 2 (매칭 시) |
| `references/anti-patterns/*.md` | 5종 검출 룰 + BLACK 재작성 지시 | Phase 4 (적용 안티패턴만) |
| `references/slide-templates/index.json` | 35 슬라이드 템플릿 메타 (color × formality) | Phase 2 (`slides`·`landing`·`assisted` 모드 HTML 케이스) |
| `references/workflow.md` | 9.5 합격선 · 4라운드 cap · 발화 톤 · `_workspace` 컨벤션 | 워크플로우 룰 참조 시 |
| `references/output-formats.md` | 카테고리별 출력 포맷 (PPT=HTML, 외=Markdown) | Phase 7 (산출물 정리) |
| `references/orchestration.md` | Phase 3·5 의사코드 상세 (Agent Teams + Sub-Agent 분기) | Phase 5 구현 참조 시 |
| `agents/roasting-{black,red,silver,blue,gold}.md` | 5인 페르소나 *공통* 행동 규약 + 팀 통신 프로토콜 | Phase 3·5 호출 시 system prompt |

## 검증된 품질 지표 (v0.2 측정값, v0.3·v0.4에서 회귀 없음)

| 게이트 | 목표 | 실측 | 출처 |
|---|---|---|---|
| 라우팅 정확도 (top-1) | ≥ 90% (Wilson 95% LB) | **98.4%** (LB 0.954) | `tests/routing/test_routing_accuracy.py` (195 phrasings × Haiku judge) |
| 안티패턴 false positive | 0% | **0%** (50/50) | `tests/anti_patterns/` (5종 × 양성 5 + 음성 5) |
| 단위/통합 테스트 | green | **97/97 pass** | `pytest -m "not slow and not network"` |
| 품질 게이트 시나리오 평균 | ≥ 9.0 | **9.17** (1/15 실측) | `tests/quality/test_quality_gate.py` (15 시나리오 풀 런은 v0.3 예정) |

베타 사용자 데이터로 v1.0 게이트(평균 ≥ 9.5, 50명 + 100 피드백) 자연 검증.

## Ecosystem (인접 스킬 통합)

`enrich:` 필드로 다른 Claude Code 스킬을 호출해 컨텍스트 보강. v0.4에서 declared:

| 케이스 / 모드 | enrich 스킬 | when |
|---|---|---|
| p25 기획안·제안서, p45 컨설팅 덱, p37 산업·시장 분석, p40 경영 진단, p76 전략 메모 | `/strategy` | strategic_question_detected |
| p28 이사회 보고서, p29 주주 서한, p33 분기 실적 리뷰, p75 DART 회사 분석 | `/dart` | company_name_detected |
| p31 IR 발표 | `/dart` | always |
| p34 IC Memo | `/dart` + `/strategy` | dart=company_name_detected, strategy=always |
| **p70 랜딩페이지, p73 웹사이트 제작, p41/42/43/45 PPT, `assisted` 모드** | **`/design-taste-frontend`** | **always (HTML 산출물)** |
| **p70 랜딩페이지** (추가) | **`/high-end-visual-design`** | **always (프리미엄 톤 보강)** |
| **p74 이미지 제작** | **`/imagegen-frontend-web` 또는 `/brandkit`** | **always (이미지 유형에 따라 자동 선택)** |
| **p59 브랜드 가이드** | **`/brandkit`** | **always** |

**v0.4 상태:** enrich 호출은 메인 Claude가 `Skill` 도구로 직접 dispatch (별도 Python 스크립트 없음). 사용자 환경에 해당 스킬이 등록되지 않았으면 조용히 건너뛰고 BLACK이 자체 판단으로 진행 (graceful degradation).

설치 가이드: `/dart`, `/strategy`는 별도 설치. taste-skill 계열(`/design-taste-frontend`, `/high-end-visual-design`, `/imagegen-frontend-web`, `/brandkit` 등)은 한 번에 설치:

```bash
npx skills add https://github.com/Leonxlnx/taste-skill
```

또는 특정 변형만:

```bash
npx skills add https://github.com/Leonxlnx/taste-skill --skill "design-taste-frontend"
```

## Design Taste Integration (taste-skill 통합 — v0.4 신설)

디자인을 갖는 산출물(HTML 페이지·웹사이트·랜딩·슬라이드 덱·이미지 프롬프트·브랜드 키트·로고 등)은 [taste-skill](https://github.com/Leonxlnx/taste-skill) 외부 스킬 계열을 자동 enrich해 anti-slop 가이드라인을 BLACK 프롬프트에 주입한다. taste-skill은 generic AI 출력 특유의 "지루하고 평범한" 디자인을 막고 레이아웃·타이포·여백·모션 품질을 끌어올리는 프레임워크다.

### 변형 매핑

| 산출물 유형 | 1순위 변형 | 2순위 (선택) |
|---|---|---|
| HTML 페이지 일반 (assisted·landing·direct·slides 모두) | `design-taste-frontend` | — |
| 프리미엄·고급 톤 랜딩 (p70 등) | `design-taste-frontend` | `high-end-visual-design` |
| 미니멀·에디토리얼 톤 (Notion/Linear 풍 요청) | `minimalist-ui` | `design-taste-frontend` |
| 브루털리스트·실험적 톤 요청 | `industrial-brutalist-ui` | — |
| 이미지 — 웹 컴프·히어로 시각 (p74 일부) | `imagegen-frontend-web` | — |
| 이미지 — 모바일 화면·플로우 | `imagegen-frontend-mobile` | — |
| 이미지 — 로고·팔레트·아이덴티티·브랜드 보드 (p74 일부, p59 전체) | `brandkit` | — |
| 잘려서 끝나는 긴 HTML 출력이 반복될 때 | `full-output-enforcement` | — |

### 동작

1. Phase 2 SEED LOAD 직후, 케이스 frontmatter의 `enrich` 블록 또는 generic_case + HTML 신호가 있으면 → 메인 Claude가 변형 1순위를 자동 선택해 `Skill` 도구로 호출.
2. taste-skill이 제공하는 디자인 가이드라인을 받아 Phase 3 BLACK 프롬프트에 다음 형식으로 첨부:
   ```
   [ENRICHMENT FROM /design-taste-frontend]
   {anti-slop 가이드라인 텍스트}
   [/ENRICHMENT]
   ```
3. BLACK은 케이스 BLACK 페르소나(예: p73의 Stripe·Linear·Vercel 톤) + taste-skill 가이드라인을 모두 흡수해 산출.
4. 미설치 시 조용히 스킵, BLACK이 케이스 페르소나만으로 진행 + 사용자에게 1회 안내:
   > 디자인 품질을 더 끌어올리려면 `npx skills add https://github.com/Leonxlnx/taste-skill` 설치를 권장합니다. 현재는 케이스 페르소나만으로 진행합니다.

### 변형 자동 선택 로직 (Claude 절차)

메인 Claude가 입력 + 케이스 정보를 보고 1순위 변형을 고른다:

- 입력에 "미니멀·심플·깔끔·Notion·Linear" → `minimalist-ui`
- 입력에 "고급·프리미엄·럭셔리·calm·spacious" 또는 p70 → `design-taste-frontend` + `high-end-visual-design`
- 입력에 "Stripe·Vercel·Linear" 또는 p73 → `design-taste-frontend`
- 입력에 "브루털·실험적·industrial" → `industrial-brutalist-ui`
- 입력에 "이미지·사진·시각·hero shot·landing visual" + 모바일 신호 없음 → `imagegen-frontend-web`
- 입력에 "이미지" + "iOS·Android·앱·모바일" → `imagegen-frontend-mobile`
- 입력에 "로고·브랜드·아이덴티티·팔레트·typography 키트" 또는 p59 → `brandkit`
- 그 외 HTML 산출물 → `design-taste-frontend` (기본)

## 한 줄 요약

`/roasting xxxxx` (또는 자연어) → 68 케이스 자동 라우팅 → BLACK 1명 + RGSB 4인 5-Color → 9.5 합격선 + 4라운드 → 산출물 3종.

**한국어 전용. 베타 v0.4.** 세부 변경 이력은 [`CHANGELOG.md`](../../CHANGELOG.md) 참조.
