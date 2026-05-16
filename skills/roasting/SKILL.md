---
name: roasting
description: 한국어 화이트칼라 산출물(이메일·보고서·PPT·웹사이트·랜딩페이지·이사회 메모·IR 자료·계약 검토·이력서·사내 공지 등 66개 케이스)을 5-Color Harness로 작성합니다. 한국 비즈니스 리더가 "써줘·다듬어줘·만들어줘·검토해줘·정리해줘" 같은 자연어 요청을 하거나 `/roasting xxxxx`로 호출하면 자동으로 케이스를 골라 BLACK 작성+RGSB 4인 채점(9.5 합격선, 4라운드)으로 산출물·평가·결정 로그를 만듭니다. PPT·웹사이트 케이스는 slide_library 템플릿 자동 결합. 한국어 전용. 영어 입력은 일반 모드 폴백.
---

# /roasting — 5-Color Harness Execution Engine

5color 사이트의 66개 케이스를 Claude Code 위에서 *집행*하는 엔진. 임원이 자연어 한 줄로 호출하면, 7-Phase 워크플로우(Pipeline + Supervisor 패턴, Phase 5만 Agent Teams)로 산출물·평가·결정 로그 3종을 출력한다.

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
2. Haiku judge 호출: top-3 case_id + 신뢰도. 구현은 `scripts/route.py:route()`.
3. `routing.json` 저장: `{top3, confidence, selected_case_id}`.
4. **분기:**
   - 신뢰도 ≥ 0.85 → top-1 자동 선택, Phase 2로.
   - 신뢰도 < 0.85 → 사용자에게 top-3 보여주고 1턴 confirm.
5. **에러 폴백:** 모든 후보 신뢰도 < 0.5 → 일반 5-Color 모드 (자산 시드 없음). 사용자에게 "이 케이스는 5color 사이트에 없습니다" 알림.

### Phase 2 — SEED LOAD

목적: 케이스 정의 + 슬라이드 템플릿 + 케이스 적용 안티패턴 로드.

처리:
1. `references/cases/{case_id}.md` 로드 (BLACK + RGSB 페르소나 정의 + GOLD 시나리오).
2. **HTML 산출물 케이스 (p41 / p42 / p43 / p45 / p70) 추가 처리:**
   - 출력 포맷이 `html`로 잡히는 케이스. PPT 4종(p41·p42·p43·p45)과 웹사이트·랜딩페이지(p70)가 여기에 속한다.
   - 동일 흐름: `references/slide-templates/index.json`의 35개 템플릿 중 톤·formality·color로 **가장 적정한 1개를 골라 그대로 베이스 HTML로 사용**. 자체 디자인 생성 금지.
   - `~/.claude/roasting/preferences/{case_id}.json` 확인.
   - 존재 → 저장된 슬라이드 ID 자동 사용.
   - 없음 → top-3 추천 + 1턴 confirm + preferences 저장.
   - 콘텐츠 주입은 `scripts/build_slide_html.py`로 슬라이드 컨테이너에 BLACK 산출물을 섹션 단위로 채운다. PPT는 슬라이드 단위(H1·H2), 랜딩(p70)은 랜딩 섹션 단위(히어로·소셜프루프·기능·CTA·FAQ 등).
3. 케이스 카테고리 따라 `references/anti-patterns/*.md` 중 적용 항목만 로드.
4. `case-context.json` 저장.

#### 2-3. Enrich Field (선택)

케이스 정의에 `enrich:` 필드가 있으면, BLACK이 작성하기 전에 외부 스킬을 호출해 컨텍스트를 보강합니다.

처리:
1. 케이스의 `enrich` 리스트 순회
2. 각 항목의 `skill` 이름으로 사용자 환경에 해당 스킬이 설치되어 있는지 확인
3. `when` 조건 평가 (Haiku judge):
   - `always`: 무조건 호출
   - `company_name_detected`: xxxxx에 회사명/티커가 포함되었는지 판정
   - `strategic_question_detected`: xxxxx가 전략적 질문(경쟁/시장/조직/M&A)인지 판정
4. 조건 통과 시 `scripts.invoke_skill.invoke(skill, xxxxx)` 호출
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

메인 Claude가 `Agent` 도구로 BLACK 서브에이전트(`agents/roasting-black.md`) 호출. 입력: xxxxx + 케이스 정의 + 슬라이드 템플릿 (p41/42/43/45/p70만) + 이전 라운드 코멘트 (Round 2+) + enrichments (Phase 2-3에서 수집된 경우). 출력: `_workspace/{session}/round-{n}/black-draft.{md|html}`.

상세 호출 의사코드는 `references/orchestration.md` 참조.

산출물 저장 후 Phase 4로.

### Phase 4 — ANTI-PATTERN CHECK (Self-correction loop)

목적: BLACK 산출물의 5종 안티패턴 검출 → 발견 시 BLACK 재작성 (라운드 카운트 안 깎임). 3-strikes 보호.

처리:
1. `scripts.anti_patterns.detect_all` 호출:
   ```python
   detected = detect_all(
       black_output=draft_text,
       case_id=case.id,
       case_category=case.category,
       case_black_tone=case.black_tone,
       case_gold_scenario=case.gold_scenario,
       user_xxxxx=xxxxx,
       judge=HaikuJudge(),
   )
   ```
2. detected가 비어있으면 → Phase 5로.
3. 검출된 각 안티패턴마다 `StrikeCounter.record(name)` 호출:
   - `ConsecutiveAntiPatternError` 발생 (3-strikes) → 사용자 보고:
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

처리 (`scripts.deliver.deliver()`):

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
5. **익명 telemetry 전송 (옵트인 시):**
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
| 슬라이드 | 2 | HTML 산출물(PPT·웹사이트) 첫 호출 | top-1 추천 | 1턴 (저장) |
| 안티패턴 무한 루프 | 4 | 동일 안티패턴 3회 | 사용자 선택 | 1턴 (예외) |
| 토론 합의 실패 | 5 | 1라운드 후 σ ≥ 0.5 | 분포 그대로 | 0 |
| 4라운드 미통과 | 6 | round=4 + score < 9.5 | 강제 출력 + 사유 | 0 |

## 에러 폴백

| 에러 | 폴백 |
|---|---|
| `TeamCreate` 사용 불가 | Sub-Agent 경로 (Phase 5.1 참조) |
| Opus 일시 불가 | RED/GOLD를 Sonnet으로 자동 다운그레이드 + 사용자 알림 |
| 라우팅 모든 후보 신뢰도 < 0.5 | 일반 5-Color 모드 (자산 시드 없음) |
| 슬라이드 템플릿 fetch 실패 | Markdown 폴백 + 경고 footer |
| `_workspace` 디스크 풀 | 가장 오래된 세션 5개 자동 삭제 + 재시도 |
| enrich 스킬 미설치 | 조용히 건너뜀, 일반 모드로 진행 |
| 영어 입력 (한국어 전용 스킬) | 일반 5-Color (자산 시드 없음). 사용자에게 한국어 요청 권유 |

## 사용 예시

| 입력 | 라우팅 결과 | 출력 |
|---|---|---|
| `/roasting 거래처 부장한테 8월 12일까지 회신 달라는 메일` | p1 외부 비즈니스 이메일 | `output.md` 200-500자 + `critique.md` |
| `이번 분기 임원 PPT 만들어줘` | p41 임원용 PPT | `output.html` (slide_library 결합) |
| `B2B SaaS 랜딩페이지 만들어줘` | p70 웹사이트·랜딩페이지 | `output.html` (slide_library 디자인 토큰 적용 한 페이지) |
| `삼성전자 분기 실적 1페이지로 정리해줘` | p73 DART 기반 회사 분석 (`/dart` enrich) | `output.md` IR 메모 |
| `신사업 검토할 때 어떤 프레임워크 써야 할까` | p74 전략 프레임워크 메모 (`/strategy` enrich) | `output.md` 1프레임워크 결정 메모 |
| `5월 조직개편 사내 공지 다듬어줘` | p16 사내 공지 | `output.md` |
| `LP 분기 레터 써줘` | p35 LP 리포트 | `output.md` |
| `공급사 사과문 검토해줘` | p2 사과문 (LEGAL_RISK_TERM 안티패턴 적용) | `output.md` + 단정 약속어 자동 검출 |

각 출력에는 항상 3종 산출물이 함께 저장됩니다: `output.{md|html}` (산출물) · `critique.md` (RGSB 4인 평가, 교재) · `reasoning.md` (BLACK 결정 로그).

## 참조 파일 인덱스

| 경로 | 내용 | 로드 시점 |
|---|---|---|
| `references/cases/_index.md` | 66 케이스 1줄 라우팅 인덱스 (~30KB) | Phase 1 |
| `references/cases/p*.md` | 케이스별 BLACK + RGSB 페르소나 + GOLD 시나리오 + (선택) `enrich:` | Phase 2 (매칭 시) |
| `references/anti-patterns/*.md` | 5종 검출 룰 + BLACK 재작성 지시 | Phase 4 (적용 안티패턴만) |
| `references/slide-templates/index.json` | 35 슬라이드 템플릿 메타 (color × formality) | Phase 2 (HTML 산출물 케이스: p41/42/43/45/p70) |
| `references/workflow.md` | 9.5 합격선 · 4라운드 cap · 발화 톤 · `_workspace` 컨벤션 | 워크플로우 룰 참조 시 |
| `references/output-formats.md` | 카테고리별 출력 포맷 (PPT=HTML, 외=Markdown) | Phase 7 (산출물 정리) |
| `references/orchestration.md` | Phase 3·5 의사코드 상세 (Agent Teams + Sub-Agent 분기) | Phase 5 구현 참조 시 |
| `agents/roasting-{black,red,silver,blue,gold}.md` | 5인 페르소나 *공통* 행동 규약 + 팀 통신 프로토콜 | Phase 3·5 호출 시 system prompt |

## 검증된 품질 지표 (v0.2)

| 게이트 | 목표 | 실측 | 출처 |
|---|---|---|---|
| 라우팅 정확도 (top-1) | ≥ 90% (Wilson 95% LB) | **98.4%** (LB 0.954) | `tests/routing/test_routing_accuracy.py` (195 phrasings × Haiku judge) |
| 안티패턴 false positive | 0% | **0%** (50/50) | `tests/anti_patterns/` (5종 × 양성 5 + 음성 5) |
| 단위/통합 테스트 | green | **97/97 pass** | `pytest -m "not slow and not network"` |
| 품질 게이트 시나리오 평균 | ≥ 9.0 | **9.17** (1/15 실측) | `tests/quality/test_quality_gate.py` (15 시나리오 풀 런은 v0.3 예정) |

베타 사용자 데이터로 v1.0 게이트(평균 ≥ 9.5, 50명 + 100 피드백) 자연 검증.

## Ecosystem (인접 스킬 통합)

`enrich:` 필드로 다른 Claude Code 스킬을 호출해 컨텍스트 보강. v0.2에서 11개 케이스가 declared:

| 케이스 | enrich 스킬 | when |
|---|---|---|
| p25 기획안·제안서, p45 컨설팅 덱, p37 산업·시장 분석, p40 경영 진단, p74 전략 메모 | `/strategy` | strategic_question_detected |
| p28 이사회 보고서, p29 주주 서한, p33 분기 실적 리뷰, p73 DART 회사 분석 | `/dart` | company_name_detected |
| p31 IR 발표 | `/dart` | always |
| p34 IC Memo | `/dart` + `/strategy` | dart=company_name_detected, strategy=always |

**v0.2 상태:** `scripts/invoke_skill.py`는 *stub* — 스킬 설치 여부 탐지 + 메타데이터 준비. 실제 Task 도구 dispatch는 v0.3에 추가. 현재는 enrich가 selected되어도 실제 호출 없이 BLACK이 자체 판단으로 진행. 사용자에게 영향 없음 (graceful degradation).

설치 가이드: 사용자가 `/dart`, `/strategy` 스킬을 별도 설치하면 v0.3 출시 시 자동으로 enrich 작동.

## 한 줄 요약

`/roasting xxxxx` (또는 자연어) → 66 케이스 자동 라우팅 → BLACK 1명 + RGSB 4인 5-Color → 9.5 합격선 + 4라운드 → 산출물 3종.

**한국어 전용. 베타 v0.2.** 세부 변경 이력은 [`CHANGELOG.md`](../../CHANGELOG.md) 참조.
