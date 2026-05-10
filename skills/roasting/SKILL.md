---
name: roasting
description: 화이트칼라 산출물(이메일·보고서·PPT·계약서·이력서·투자 메모·사내 공지·이사회 보고서·IR 자료 등 63개 케이스) 작성을 5-Color Harness 방법론으로 수행. 임원·비즈니스 리더가 자연어 한 줄(/roasting xxxxx 또는 일반 요청)로 호출하면 케이스 자동 매칭 후 BLACK 수행자가 작성하고 RED·SILVER·BLUE·GOLD 4인이 토론 채점. 9.5 합격선까지 최대 4라운드 자동 반복. PPT 케이스에서 slide_library 35개 템플릿 자동 결합. 안티패턴 5종(환각 수치·모호 CTA·누락된 GOLD 후크·톤 미스매치·법무 단정어) 자동 검출. 산출물·평가 코멘트·결정 로그 3종 출력.
---

# /roasting — 5-Color Harness Execution Engine

5color 사이트의 63개 케이스를 Claude Code 위에서 *집행*하는 엔진. 임원이 자연어 한 줄로 호출하면, 7-Phase 워크플로우(Pipeline + Supervisor 패턴, Phase 5만 Agent Teams)로 산출물·평가·결정 로그 3종을 출력한다.

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

목적: xxxxx → 63 케이스 중 1개 매칭.

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
2. **PPT 카테고리 (p41/p42/p43/p45) 추가 처리:**
   - `~/.claude/roasting/preferences/{case_id}.json` 확인.
   - 존재 → 저장된 슬라이드 ID 자동 사용.
   - 없음 → top-3 슬라이드 추천 + 1턴 confirm + preferences 저장.
3. 케이스 카테고리 따라 `references/anti-patterns/*.md` 중 적용 항목만 로드.
4. `case-context.json` 저장.

### Phase 3 — BLACK DRAFT (Producer)

목적: 케이스 BLACK 페르소나 캐스팅으로 산출물 1차 작성.

호출 방식 (메인 Claude가 직접 수행):

```
Agent(
  subagent_type="general-purpose",   # roasting-black.md를 system prompt로 주입
  description="BLACK draft for {case_id} round {n}",
  prompt=f"""
You are following agents/roasting-black.md. Use the case persona from
references/cases/{case_id}.md (BLACK section) as your character casting.

Inputs:
- xxxxx: {user_xxxxx}
- 케이스 정의 (전문): {case_md_content}
- 슬라이드 템플릿 (PPT만): {slide_meta_json}
- 이전 라운드 RGSB 코멘트 (Round 2+): {prev_critiques_md}

산출물 작성. Markdown 또는 HTML. 자평·메타 코멘트 금지.
출력 위치: _workspace/{session}/round-{n}/black-draft.{ext}
"""
)
```

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

### Phase 5 — RGSB REVIEW (Agent Teams)

> **구현은 PR 9 (sub-agent fallback) → PR 10 (Agent Teams)에서 채움.** stub.

### Phase 6 — LOOP

> **구현은 PR 11에서 채움.**

### Phase 7 — DELIVER

> **구현은 PR 11에서 채움.**

## 컨펌 시점

| 시점 | Phase | 트리거 | 디폴트 | 부담 |
|---|---|---|---|---|
| 라우팅 | 1 | 신뢰도 < 0.85 | top-1 자동 | 1턴 |
| 슬라이드 | 2 | PPT 첫 호출 | top-1 추천 | 1턴 (저장) |
| 안티패턴 무한 루프 | 4 | 동일 안티패턴 3회 | 사용자 선택 | 1턴 (예외) |
| 토론 합의 실패 | 5 | 1라운드 후 σ ≥ 0.5 | 분포 그대로 | 0 |
| 4라운드 미통과 | 6 | round=4 + score < 9.5 | 강제 출력 + 사유 | 0 |

## 워크플로우 상세 룰

`references/workflow.md` 참조 (9.5 합격선·4라운드 캡·발화 톤·_workspace 컨벤션).

## 출력 포맷

`references/output-formats.md` 참조 (PPT 카테고리 = HTML, 그 외 = Markdown).

## 안티패턴

`references/anti-patterns/*.md` 참조 (5종).

## 케이스 카탈로그

`references/cases/_index.md` (라우팅용 인덱스), `references/cases/p*.md` (케이스별 상세).

## 에이전트

`agents/{black,red,silver,blue,gold}.md` (5종 페르소나 정의).
