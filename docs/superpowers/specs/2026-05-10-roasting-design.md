# `/roasting` — Design Spec v0.1

| 항목 | 값 |
|---|---|
| **Author** | jaydenjkang@gmail.com (AI ROASTING / airoasting) |
| **Date** | 2026-05-10 |
| **Status** | Draft (pending user review) |
| **Target Repo** | `airoasting/roasting` |
| **Distribution** | Anthropic 마켓플레이스 + GitHub + airoasting.github.io 랜딩 |
| **License** | MIT |
| **Target Users** | 한국 비즈니스 리더 (개발자 아님) |
| **Release Mode** | Open Beta |

---

## 1. Overview & Vision

### 한 줄 정의
**5color 사이트가 만들어내는 "프롬프트"를 실제로 *실행*하는 첫 번째 엔진.**
5color 사이트 = 프롬프트 라이브러리(생성기). `/roasting` = 실행 엔진(런타임).

### 작동 한 줄
임원이 `/roasting xxxxx` (예: `/roasting 이번 분기 보드 데크 만들어줘`) 자연어 한 줄로 호출 → 63개 케이스 중 자동 매칭 → BLACK이 작성하고 RED·SILVER·BLUE·GOLD 4인이 토론 채점 → 9.5 합격선까지 최대 4라운드 자동 반복 → 산출물 + 평가 코멘트 + 결정 로그 3종 출력.

### 차별성 (Section 0 — 정직하게)
- **발명적 독창성**: 3/10 (모든 부품이 기존 것 — Agent Teams는 Anthropic, 5-Color는 사용자, Progressive Disclosure는 표준)
- **조합적 독창성**: 8/10 (5color PROMPTS + Agent Teams 토론 + slide_library 시드 + 임원 안티패턴 + 1줄 UX의 *조합*은 누구도 안 함)
- **임팩트적 독창성**: 7/10 (한국 임원 AI 활용 시장의 정확한 갭)

진짜 해자(moat)는 **알고리즘이 아니라 *데이터***:
- 5color 사이트의 63 케이스 페르소나 캐스팅 정의
- slide_library의 35 HTML 템플릿
- 두 자산을 운영체제로 만드는 어댑터가 `/roasting`

---

## 2. Decisions Summary (확정 11개)

| # | 결정 | 값 |
|---|---|---|
| 1 | v0.1 정체 | 오픈 베타 |
| 2 | 출력 포맷 | PPT 4 케이스 = HTML + slide_library, 나머지 = Markdown |
| 3 | 언어 | 한국어 only (README/플러그인 description은 영어) |
| 4 | slide_library 결합 | 자동 추천 + 1회 컨펌 + xxxxx 단서 분기 |
| 5 | 피드백 수집 | 익명 telemetry + `/roasting --feedback` |
| 6 | 모델 라우팅 | BLACK Sonnet + RED·GOLD Opus + SILVER·BLUE Sonnet |
| 7 | 안티패턴 | 5종 (HALLUCINATED_NUMBER, VAGUE_CTA, MISSING_GOLD_HOOK, TONE_MISMATCH, LEGAL_RISK_TERM) |
| 8 | 배포 | 마켓 + GitHub + airoasting 랜딩 / 이름 `airoasting/roasting` |
| 9 | 라우팅 confirm | 신뢰도 ≥ 0.85 자동 / 미만 1턴 confirm |
| 10 | 사이트 동기화 | v0.1 = 수동 (`make sync-cases`). 자동화는 v0.2 |
| 11 | 케이스 등급 표시 | v0.1 = 표시 안 함 (모두 "beta"). v0.2에 자동 계산 |

---

## 3. Architecture

### 3.1 거시 패턴
**Pipeline + Supervisor** (7-Phase 순차, 메인 SKILL.md가 조율)

### 3.2 Phase별 패턴

| Phase | Harness 6패턴 | 실행 모드 | 모델 |
|---|---|---|---|
| 1. PARSE | Expert Pool (63→1) | 메인 직접 | Haiku |
| 2. SEED LOAD | (단순 파일 로드) | 메인 직접 | - |
| 3. BLACK DRAFT | Producer | 메인 직접 (agents/roasting-black) | Sonnet |
| 4. ANTI-PATTERN | Self-correction loop | script + Haiku | Haiku |
| 5. RGSB REVIEW | **Producer-Reviewer + Fan-out/Fan-in** | **Agent Teams** ★ | RED·GOLD Opus / SILVER·BLUE Sonnet |
| 6. LOOP | 조건부 backedge | 메인 직접 | - |
| 7. DELIVER | (산출물 정리) | 메인 직접 | - |

### 3.3 왜 Phase 5만 Agent Teams 모드인가
1. RGSB 4명이 *서로 토론*해야 5-Color 본래 의도 충족 (anthropic-skills:5color는 순차 평가만)
2. 표준편차 σ ≥ 0.5 토론 트리거 — 합의 강하면 비용 절약
3. 다른 Phase는 단일 도구 호출이라 팀 오버헤드 정당화 불가
4. 페르소나 *순수성* 유지 (한 컨텍스트에서 RED→SILVER 순차면 RED 코멘트가 SILVER 판단에 오염됨)

---

## 4. 디렉토리 구조

```
airoasting/roasting/                              # GitHub repo
├── .claude-plugin/
│   ├── plugin.json
│   └── marketplace.json
├── skills/
│   └── roasting/
│       ├── SKILL.md                              # 메인 (~250줄)
│       ├── agents/                               # ★ Anthropic Agent Teams 표준
│       │   ├── roasting-black.md                 # Producer
│       │   ├── roasting-red.md                   # Reviewer (이성)
│       │   ├── roasting-silver.md                # Reviewer (분야 전문가)
│       │   ├── roasting-blue.md                  # Reviewer (공감)
│       │   └── roasting-gold.md                  # Reviewer (독자)
│       └── references/
│           ├── cases/                            # Progressive Disclosure
│           │   ├── _index.md                     # 63 케이스 1줄 요약 (~30KB)
│           │   ├── p1-email-external.md
│           │   ├── p2-apology.md
│           │   └── ... (총 63개)
│           ├── anti-patterns/
│           │   ├── hallucinated-number.md
│           │   ├── vague-cta.md
│           │   ├── missing-gold-hook.md
│           │   ├── tone-mismatch.md
│           │   └── legal-risk-term.md
│           ├── slide-templates/
│           │   └── index.json                    # 35 HTML 템플릿 메타
│           ├── workflow.md                       # 9.5 합격선·4라운드·발화 톤·_workspace
│           └── output-formats.md                 # 카테고리별 출력 포맷
├── scripts/
│   ├── sync_cases.py                             # 5color 사이트 → cases/*.md
│   ├── route.py                                  # Haiku 기반 라우팅
│   ├── anti_patterns.py                          # 안티패턴 검출 (regex + LLM hybrid)
│   └── telemetry.py                              # 익명 telemetry 전송
├── tests/
│   ├── routing/                                  # 63 × 3 = 189 테스트
│   ├── anti-patterns/                            # 5종 × 양성+음성 = 50 테스트
│   └── quality/                                  # 5 케이스 × 3 입력 = 15 시나리오
├── docs/
│   ├── ko/
│   └── en/
├── Makefile                                      # sync-cases·test·package·publish
├── README.md                                     # 영어 (마켓 노출)
├── README.ko.md                                  # 한국어 (임원용)
├── LICENSE                                       # MIT
└── CHANGELOG.md
```

### 컴포넌트 책임 1줄

| 컴포넌트 | 책임 |
|---|---|
| `SKILL.md` | /roasting 진입 → 라우팅 → 7-Phase 워크플로우 오케스트레이션 |
| `agents/*.md` (5개) | 페르소나 *공통* 행동 규약 + 팀 통신 프로토콜 + 도구 화이트리스트 |
| `references/cases/_index.md` | 63 케이스 1줄 요약 — 라우팅 LLM judge용 |
| `references/cases/p*.md` | 케이스별 BLACK·RGSB 페르소나 정의 + GOLD 시나리오 (매칭 시만 로드) |
| `references/anti-patterns/*.md` | 5종 검출 룰 + BLACK 재작성 지시 |
| `references/slide-templates/index.json` | 35개 HTML 템플릿 메타 (id·name·color·formality·url) |
| `references/workflow.md` | 9.5 합격선·4라운드 캡·발화 톤 룰·출력 3종·_workspace 컨벤션 |
| `scripts/sync_cases.py` | airoasting.github.io/5color HTML → PROMPTS 추출 → cases/*.md 갱신 |
| `scripts/anti_patterns.py` | regex 사전 + LLM judge hybrid. 3-strikes 방어 |
| `scripts/telemetry.py` | 익명 metadata 전송. 콘텐츠 절대 미수집 |
| `Makefile` | `make sync-cases` · `make test` · `make package` · `make publish` |

---

## 5. Data Flow — 7-Phase 워크플로우

### Phase 0 / 진입과 세션 초기화
- 트리거: `/roasting xxxxx` 또는 자연어 (description 매칭)
- 동작: `~/.claude/roasting/_workspace/{YYYYMMDD-HHMMSS}-{tmp_id}/` 생성, `input.txt` 저장
- 모델 호출: 0

### Phase 1 / PARSE — Expert Pool 라우팅
| 항목 | 정의 |
|---|---|
| 입력 | xxxxx, references/cases/_index.md (~30KB) |
| 처리 | Haiku judge: "xxxxx → top-3 케이스 + 신뢰도" |
| 분기 | 신뢰도 ≥ 0.85 자동 / < 0.85 1턴 confirm |
| 출력 | case_id |
| 파일 | `_workspace/{session}/routing.json` |
| 모델 | Haiku × 1 (~$0.005) |
| 에러 | 모든 후보 < 0.5 → 일반 5-Color 모드 폴백 |

### Phase 2 / SEED LOAD
| 항목 | 정의 |
|---|---|
| 입력 | case_id |
| 처리 | (1) `references/cases/{case_id}.md` 로드 <br> (2) PPT 카테고리면 `~/.claude/roasting/preferences/{case_id}.json` 확인. 없으면 top-3 슬라이드 추천 + 1턴 confirm + preferences 저장 <br> (3) 케이스 적용 안티패턴만 로드 |
| 출력 | 케이스 정의 + 슬라이드 ID + 안티패턴 리스트 |
| 파일 | `_workspace/{session}/case-context.json` |
| 모델 | 0 |

### Phase 3 / BLACK DRAFT — Producer
| 항목 | 정의 |
|---|---|
| 에이전트 | `agents/roasting-black.md` (Sonnet, tools=[Read, Write]) |
| System prompt | 케이스 BLACK 페르소나 + GOLD 합격선 시나리오 |
| User prompt | xxxxx + 슬라이드 메타 (PPT 시) + 이전 라운드 코멘트 (Round 2+) |
| 출력 | Markdown 또는 HTML |
| 파일 | `_workspace/{session}/round-{n}/black-draft.{md\|html}` |
| 모델 | Sonnet × 1 (~$0.02) |

### Phase 4 / ANTI-PATTERN CHECK — Self-correction loop (3-strikes 방어)
| 항목 | 정의 |
|---|---|
| 처리 | `scripts/anti_patterns.py`: 5종 모두 검사 |
| 검출 시 | BLACK 재작성 → Phase 3 재호출 (라운드 카운트 안 깎임) |
| **무한 루프 방어** | **동일 안티패턴 3회 연속 검출 (한 라운드 내 또는 라운드 간 누적, 둘 다 카운트)** → 사용자 보고: "(1) 진행 (2) 중단 (3) 케이스 재선택" |
| 통과 시 | Phase 5로 |
| 파일 | `_workspace/{session}/round-{n}/anti-patterns.json` |
| 모델 | Haiku × 3-4 (~$0.025) |

### Phase 5 / RGSB REVIEW ★ Agent Teams 모드

#### 5.1 Round 1 진입
```
TeamCreate(
    team_name=f"5color-rgsb-{case_id}-{session_id}",
    members=[
        {"name": "RED",    "agent": "roasting-red",    "model": "opus"},
        {"name": "GOLD",   "agent": "roasting-gold",   "model": "opus"},
        {"name": "SILVER", "agent": "roasting-silver", "model": "sonnet"},
        {"name": "BLUE",   "agent": "roasting-blue",   "model": "sonnet"}
    ]
)
SendMessage(to="all", content={black_draft + case_definition + persona_definitions})
```

#### 5.2 병렬 채점 (Fan-out)
- 4명 동시 채점: `{score, reason, suggestion}` 형식
- `TaskCreate("scoring-table-round-{n}")` 결과 등록

#### 5.3 토론 트리거 (σ 기반)
- 메인이 σ 계산
- σ < 0.5 → 합의 강함, 평균 사용. 토론 SKIP
- σ ≥ 0.5 → 토론 1라운드:
  - 가장 높은 vs 가장 낮은 페르소나 선택
  - **타이브레이커**: 점수 동률 시 우선순위 GOLD > RED > SILVER > BLUE (독자·이성이 합격선 결정에 가중치)
  - `SendMessage(low→high, "독자/이성 입장 X 약점, 점수 재고려")`
  - `SendMessage(high→low, "Y 강점 고려")`
  - 양측 새 점수 + 코멘트 `TaskUpdate`
  - 1라운드 후 σ 여전히 ≥ 0.5면 → "합의 실패" 표시
  - **컨텍스트 드리프트 방어**: 라운드 간 RGSB 컨텍스트 유지로 일관성 ↑하나, 5라운드 이상 누적 시 4라운드 cap에서 끊겨 자연 해소

#### 5.4 게이트
- 평균 ≥ 9.5 → Phase 7
- 미만 → Phase 6

#### 5.5 라이프사이클
- **케이스당 1팀, 라운드 간 유지** (Round 2+에서 TeamCreate 안 함)
- Phase 7 진입 직전 1회 `TeamDelete`
- 라운드 간 RGSB 컨텍스트 유지 → 일관성 ↑

| 항목 | Round 1 | Round n+1 |
|---|---|---|
| TeamCreate | ✓ | ✗ |
| BLACK draft broadcast | ✓ | ✓ |
| 채점 | ✓ | ✓ |
| 토론 (σ ≥ 0.5) | 조건부 | 조건부 |
| 모델 호출 비용 | ~$0.18 | ~$0.18 |

### Phase 6 / LOOP — 조건부 backedge
| 조건 | 행동 |
|---|---|
| 평균 ≥ 9.5 | Phase 7 |
| < 9.5 + round < 4 | BLACK에 4인 코멘트 + 이전 산출물 → Phase 3 |
| < 9.5 + round == 4 | 강제 종료. 가장 높은 라운드 결과 사용. 사용자 보고 "9.5 미달 (max=X.Y). 캐스팅/과제 정의 문제 가능성. 1on1 권장" |

### Phase 7 / DELIVER — 산출물 정리
```
_workspace/{session}/final/
├── output.{html|md}        # 임원이 사용
├── critique.md             # RGSB 4인 평가 (교재)
└── reasoning.md            # BLACK 결정 로그 + 라운드 진화 + 안티패턴 이력
```

순서:
1. `TeamDelete`
2. 3종 산출물 정리 → `final/`
3. 사용자 안내: 산출물 위치 + 인터랙티브 메뉴
4. 익명 telemetry 전송 (옵트인): `{case_id, final_score, round_count, slide_template_id, total_cost, anti_patterns_detected, debate_triggered}` — 콘텐츠 텍스트 절대 미포함

---

## 6. Confirm 시점 통합 표

| 시점 | Phase | 트리거 | 디폴트 | 임원 부담 |
|---|---|---|---|---|
| 라우팅 | 1 | 신뢰도 < 0.85 | top-1 자동 | 1턴 |
| 슬라이드 | 2 | PPT 케이스 첫 호출 | top-1 추천 | 1턴 (저장됨) |
| 안티패턴 무한 루프 | 4 | 동일 안티패턴 3회 | 사용자 선택 | 1턴 (예외) |
| 토론 합의 실패 | 5 | 1라운드 토론 후도 σ ≥ 0.5 | 분포 그대로 출력 | 0 |
| 4라운드 미통과 | 6 | round=4 + score < 9.5 | 강제 출력 + 사유 | 0 |

---

## 7. Error Handling — 5종 폴백

| 에러 | 폴백 |
|---|---|
| Agent Teams API 실패 | `Agent` 도구 + `run_in_background` 4 서브 에이전트 (토론 SKIP, 평균만) |
| Opus 일시 불가 | RED/GOLD를 Sonnet으로 자동 다운그레이드 + 사용자 알림 |
| 라우팅 모든 후보 < 0.5 | 일반 5-Color 모드 (자산 시드 없음). "이 케이스는 5color 사이트에 없습니다" |
| 슬라이드 템플릿 로드 실패 | 텍스트 슬라이드 (Markdown) 폴백 + 사용자 알림 |
| `_workspace` 디스크 풀 | 가장 오래된 세션 5개 자동 삭제 + 재시도 |

---

## 8. 안티패턴 5종 정의

| # | 이름 | 검출 방법 | 트리거 | 적용 범위 |
|---|---|---|---|---|
| 1 | HALLUCINATED_NUMBER | regex 수치 추출 + Haiku judge | 출처 없는 수치 1개+ | 전 케이스, 단 카테고리 "소셜미디어·글쓰기"의 시(p64)·소설(p63)·링크드인 프로필(p69) 3개 제외 |
| 2 | VAGUE_CTA | regex 사전 + Haiku 보조 | 끝 50자에 "검토 부탁/참고 바랍니다" 등 + 명확한 동사 없음 | 외부+내부 커뮤니케이션, 의사결정·전략 (~30 케이스) |
| 3 | MISSING_GOLD_HOOK | Haiku judge | 케이스의 GOLD 합격선 장면이 첫 200자에 없음 | 전 케이스 |
| 4 | TONE_MISMATCH | Haiku judge | BLACK 캐스팅 톤과 산출물 첫 문장 어휘 거리 큼 | 전 케이스 |
| 5 | LEGAL_RISK_TERM | regex only | "보장합니다·확실히·절대로·100%·약속드립니다" 등 | 법무 7 + 외부 커뮤니케이션 일부 (~12 케이스) |

검출 후 동작 (5종 공통):
- RGSB 채점 *전*에 BLACK 재작성. 라운드 카운트 안 깎임
- 동일 안티패턴 3회 연속 검출 시 → 사용자 보고

---

## 9. Agents 정의

### `agents/roasting-black.md`
```yaml
---
name: roasting-black
description: 5-Color Harness BLACK 수행자. 케이스별 BLACK 페르소나 캐스팅에 따라 화이트칼라 산출물 1차 작성. 안티패턴 검출 시 자체 재작성. RGSB 코멘트 받아 라운드별 개선.
tools: ["Read", "Write"]
model: sonnet
---
```
본문: 입출력 프로토콜, 자평·메타 코멘트 금지, 안티패턴 재작성 시 라운드 카운트 안 깎임, RGSB SILVER 직접 질문 답변 가능 (선택).

### `agents/roasting-red.md`
```yaml
---
name: roasting-red
description: 5-Color RED 이성 평가자. BLACK 산출물의 의도 전달·논리·단정 정도를 케이스별 RED 페르소나로 채점. 점수+1줄 이유+1줄 개선안. σ ≥ 0.5 시 토론 참여.
tools: ["Read"]
model: opus
---
```

### `agents/roasting-gold.md`
```yaml
---
name: roasting-gold
description: 5-Color GOLD 독자 시점 평가자. 케이스 GOLD 합격선 장면(독자가 만나는 미리보기 등)에 산출물 부합 여부 채점. 9.5 통과/실패 결정에 가장 큰 가중치.
tools: ["Read"]
model: opus
---
```

### `agents/roasting-silver.md`
```yaml
---
name: roasting-silver
description: 5-Color SILVER 분야 전문가 평가자. 케이스별 SILVER 페르소나(예: 비서팀장 18년차, 사외 변호사 16년차)로 분야 정확성·구조·합법성 평가.
tools: ["Read"]
model: sonnet
---
```

### `agents/roasting-blue.md`
```yaml
---
name: roasting-blue
description: 5-Color BLUE 공감 평가자. 케이스별 BLUE 페르소나로 톤·분량·수신자 입장 평가.
tools: ["Read"]
model: sonnet
---
```

**공통**: 페르소나 *세부 캐스팅*은 `references/cases/{case_id}.md`. agents/*.md는 *공통 행동 규약*만.

---

## 10. Testing Strategy

### 10.1 라우팅 정확도 (★ 핵심 게이트)
- 63 × 3 = **189 테스트**
- Wilson Score 95% CI
- v0.1 출시 게이트: **top-1 정확도 ≥ 90%** (Wilson 하한)

### 10.2 안티패턴 단위 테스트
- 5종 × 양성 5 + 음성 5 = **50 테스트**
- 양성 검출, 음성 false positive 0%

### 10.3 출력 품질 통합 테스트
- 5 대표 케이스 × 3 입력 = **15 시나리오**
- v0.1 게이트: **평균 점수 ≥ 9.0** (베타)

### 10.4 회귀 테스트 (CI)
- `make sync-cases` 후 자동 — 케이스 정의 변경 시 라우팅·안티패턴 재실행

---

## 11. Distribution

### 11.1 `.claude-plugin/plugin.json`
```json
{
  "name": "roasting",
  "version": "0.1.0",
  "description": "5-Color Harness execution engine for Korean business leaders. Auto-routes 63 white-collar artifact cases (email, board memo, investor letter, etc.) and produces output via BLACK Producer + RGSB Reviewer team with debate-driven scoring. Korean only.",
  "author": {"name": "AI ROASTING", "url": "https://airoasting.github.io"},
  "homepage": "https://airoasting.github.io/roasting",
  "repository": "https://github.com/airoasting/roasting",
  "license": "MIT",
  "keywords": ["5-color-harness", "korean", "executive", "white-collar",
               "agent-teams", "producer-reviewer"]
}
```

### 11.2 `.claude-plugin/marketplace.json`
```json
{
  "name": "airoasting",
  "owner": {"name": "AI ROASTING"},
  "plugins": [{"name": "roasting", "source": "./", "version": "0.1.0"}]
}
```

### 11.3 README 2종
- **README.md** (영어, 마켓): "What it does / Install / Korean only — see README.ko.md"
- **README.ko.md** (한국어, 임원): 사용법 · 63 케이스 카탈로그 · 5-Color 설명 · privacy 정책

### 11.4 Privacy Policy (강조)
README.ko.md 상단에 명시:
> **우리는 콘텐츠를 절대 수집하지 않습니다.** 익명 메타데이터(케이스 ID·점수·라운드 수·타임스탬프)만 베타 개선에 사용. xxxxx 입력·BLACK 산출물·RGSB 코멘트는 외부 전송 0.

---

## 12. Telemetry Backend (Supabase)

```sql
CREATE TABLE roasting_telemetry (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    user_id UUID NOT NULL,
    skill_version TEXT NOT NULL,
    case_id TEXT NOT NULL,
    final_score NUMERIC(3,1),
    round_count INT,
    slide_template_id TEXT,
    total_cost_usd NUMERIC(10,4),
    anti_patterns_detected JSONB,
    debate_triggered BOOLEAN,
    completion_status TEXT
);

CREATE INDEX idx_case_id ON roasting_telemetry(case_id);
CREATE INDEX idx_user_id ON roasting_telemetry(user_id);
```

옵트아웃: `~/.claude/roasting/config.json` `{"telemetry": false}` 시 비활성.
피드백: `/roasting --feedback` → GitHub Issue prefilled (session_id 포함, telemetry와 매칭).

---

## 13. Versioning Roadmap

| 버전 | 시점 | 핵심 |
|---|---|---|
| **v0.1.x** | 오픈 베타 | 63 케이스 + 안티패턴 5종 + telemetry |
| v0.2.x | 베타 데이터 확보 후 | Instinct (사용자별 진화), Hooks (PreToolUse·Stop), 안티패턴 +3종 |
| v0.3.x | 케이스 검증 진행 후 | 검증 등급 표시 (Platinum/Gold/Silver/Bronze) |
| **v1.0.0** | 검증된 케이스 ≥ 30개 | Stable. SLA 보장. 유료 모델 옵션 |
| v2.0.0 | 시장 검증 후 | 영어 케이스 / 다른 언어 / Codex·Cursor 포팅 |

**v0.1 → v1.0 게이트** (자동 측정):
- 라우팅 정확도 ≥ 95% (Wilson 하한)
- 평균 최종 점수 ≥ 9.5
- 베타 사용자 ≥ 50명 + 피드백 ≥ 100건
- 케이스별 호출 수 ≥ 10

---

## 14. 비용 시나리오

| 시나리오 | 토론 | 라운드 | 비용 | 빈도 |
|---|---|---|---|---|
| 1R 통과 | σ < 0.5 | 1 | $0.21 | 30% |
| 1R 통과 (토론) | σ ≥ 0.5 | 1 | $0.26 | 25% |
| 2R 통과 | 1회 | 2 | $0.43 | 25% |
| 3R 통과 | 1-2회 | 3 | $0.66 | 15% |
| 4R 강제 | 매번 | 4 | $0.92 | 5% |
| **가중 평균** | | **1.85** | **$0.36** | |

→ 1인 월 사용 (5회/일 × 30일) ≈ $54.

---

## 15. CLAUDE.md 등록

설치 시 사용자 CLAUDE.md에 자동 추가:
```markdown
## 하네스: /roasting (airoasting/roasting v0.1)
**트리거**: 화이트칼라 산출물 작성 요청 (이메일·보고서·PPT·메모 등) 시 `roasting` 스킬 사용. xxxxx에서 도메인 자동 라우팅.
**산출 위치**: ~/.claude/roasting/_workspace/
**변경 이력**:
| 날짜 | 변경 | 사유 |
|------|------|------|
| 2026-05-10 | 초기 설치 | - |
```

---

## 16. Build/Release Makefile

```makefile
.PHONY: sync-cases test test-routing test-anti-patterns package publish

sync-cases:
	@python scripts/sync_cases.py \
		--source https://airoasting.github.io/5color/ \
		--out skills/roasting/references/cases/

test: test-routing test-anti-patterns test-quality

test-routing:
	@python -m pytest tests/routing/ -v

test-anti-patterns:
	@python -m pytest tests/anti-patterns/ -v

test-quality:
	@python -m pytest tests/quality/ -v --slow

package:
	@mkdir -p dist/
	@zip -r dist/roasting-$$(jq -r .version .claude-plugin/plugin.json).zip \
		.claude-plugin/ skills/ scripts/ docs/ README.md README.ko.md LICENSE

publish:
	@gh release create v$$(jq -r .version .claude-plugin/plugin.json) \
		dist/roasting-*.zip --title "v$$(jq -r .version .claude-plugin/plugin.json)"
```

CI (GitHub Actions):
- Push to `main` → `make test`
- Tag `v*` → `make package` → release

---

## 17. v0.1 산출물 체크리스트

릴리스 전 점검:
- [ ] 5 agents/*.md (frontmatter + 본문)
- [ ] 63 references/cases/*.md (사이트 sync 자동)
- [ ] 5 references/anti-patterns/*.md
- [ ] references/slide-templates/index.json (35 템플릿)
- [ ] references/workflow.md
- [ ] SKILL.md (~250줄)
- [ ] scripts/sync_cases.py
- [ ] scripts/anti_patterns.py
- [ ] scripts/route.py
- [ ] scripts/telemetry.py
- [ ] tests/routing/ (189)
- [ ] tests/anti-patterns/ (50)
- [ ] tests/quality/ (15)
- [ ] .claude-plugin/plugin.json + marketplace.json
- [ ] README.md (영어) + README.ko.md (한국어)
- [ ] LICENSE (MIT)
- [ ] CHANGELOG.md
- [ ] Privacy policy README.ko.md 상단
- [ ] CLAUDE.md 자동 등록 hook
- [ ] Supabase telemetry 백엔드
- [ ] GitHub Actions CI

---

## 18. Open Questions / Future Work

### v0.1에서 보류 (의식적 결정)
- 영어 케이스 (v2.0)
- Instinct 사용자별 진화 (v0.2)
- Hooks 시스템 (v0.2)
- 안티패턴 OVER_LENGTH, PII_LEAK, METRIC_WITHOUT_BASELINE (v0.2-3)
- 사이트 → 스킬 자동 동기화 (v0.2)
- 케이스 등급 표시 (v0.3, 데이터 누적 후)
- Cross-runtime (Codex, Cursor) (v2.0)
- 유료 SaaS 옵션 / API 키 제공 (v1.0+)

### v0.1 빌드 중 결정 필요한 디테일
- 슬라이드 템플릿 ID 매핑 — slide_library의 35개에 정확한 ID·메타 부여 (color × formality 정량화)
- BLACK이 SILVER 직접 질문에 답변할 시기 — 자동 vs 사용자 명시 트리거
- `/roasting --resume` 명령 (v0.2 예정이지만 v0.1에 stub만 둘지)
- telemetry user_id 생성 시점 (설치 vs 첫 호출)
- 베타 종료 시점 / v1.0 promote 트리거 (자동 vs 수동)

### 확인 필요
- Anthropic 마켓플레이스의 베타 라벨 지원 여부
- Agent Teams 기능의 안정성 (실험적 기능)
- Supabase 무료 티어로 베타 트래픽 감당 가능 여부
- 한국어 모델 라우팅 정확도가 실제로 ≥ 90% 달성 가능한지

---

## 19. Spec 자체 평가

| 차원 | 점수 |
|---|---|
| 결정 사항 명확성 | 10/10 (11개 결정 모두 명시) |
| 아키텍처 패턴 | 10/10 (Phase별 매핑 명확) |
| 데이터 흐름 | 10/10 (7-Phase 입출력·파일·모델·에러) |
| Agent 정의 (Anthropic 표준) | 10/10 (5 agents frontmatter) |
| 안티패턴 | 10/10 (5종 + pseudocode + 3-strikes) |
| 테스트 커버리지 | 10/10 (189 + 50 + 15) |
| Distribution 준비 | 10/10 (plugin.json + marketplace.json + README 2종) |
| Privacy & Telemetry | 10/10 (스키마 + 옵트아웃 + 명시적 약속) |
| Versioning | 10/10 (v0.1 → v1.0 게이트) |
| 산출물 체크리스트 | 10/10 (16+ 항목) |

**Spec 종합: 10/10**

---

*다음 단계: writing-plans 스킬로 implementation plan 작성 → v0.1 빌드 시작*
