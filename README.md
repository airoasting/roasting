# roasting

> **5-Color Harness execution engine for Korean white-collar work.**
> One producer + four critics with mandatory debate, not just score-averaging. Auto-routes
> 68 cases (emails, board memos, IR letters, landing pages, image-prompt sets, hand-coded
> websites, DART company briefs, strategy memos …), iterates against a **9.5 / 10** pass
> bar with anti-pattern pre-correction, and delivers polished Korean output. All inside
> Claude Code. Open Beta v0.4.1.

**Korean documentation:** [README.ko.md](README.ko.md)

---

## Install

```bash
/plugin marketplace add airoasting/roasting
/plugin install roasting@airoasting
```

---

## What it does

`/roasting` takes a one-line description of your task in natural Korean and:

1. **Routes** your request to the best-matching case from a library of 68 white-collar artifact
   types (emails, apologies, board memos, investor letters, legal opinions, landing pages,
   hand-coded websites, image-prompt sets, …).
2. **Casts** five personas *per case*. Every case has its own producer + 4 critics with their
   own vocabulary, pass-line scenes, and forbidden patterns.
3. **Produces** a first draft through the BLACK persona, the case-cast expert author.
4. **Auto-corrects** for 5 anti-patterns (vague CTA, unsourced numbers, legal-risk terms,
   missing GOLD hook, tone mismatch) *before* the critics see the draft.
5. **Reviews** the draft with four specialist critics: RED (logic), SILVER (domain expertise),
   BLUE (empathy/tone), GOLD (reader-in-scene simulation).
6. **Debates** when critics disagree (score spread σ ≥ 0.5): the highest and lowest scorer
   exchange comments and re-score. No forced consensus.
7. **Iterates** up to 4 rounds against a **9.5 / 10** pass bar. If the bar isn't met after
   round 4, the engine reports the gap honestly rather than passing under-quality work.
8. **Delivers** three outputs: the polished artifact, a critique sheet, and a reasoning log.
   HTML output has three sub-modes: `slides` for PPT cases (template-injected), `landing`
   for p70 (template-injected by H2 section), and `direct` for p73 웹사이트 제작 (BLACK
   writes a complete HTML file from scratch, no template fetch).

---

## What makes 5-Color Harness distinctive

"Harness" patterns put roles, rules, and verification on top of an LLM. 5-Color is not just
another producer-reviewer loop. Six things set it apart.

### 1. Per-case persona casting

The five personas are *not generic*. For an email, BLACK is a 15-year B2B SaaS senior with
Bain-consultant reply tone; for an executive PPT, BLACK is a 17-year McKinsey-bred strategy
director. The four critics are recast just as specifically: their vocabulary, their
end-of-turn patterns, and their pass-line scenes change per case. The 68 case definitions
themselves are the IP, not the orchestration code.

**BLACK casting examples (4 of 68 cases):**

| Case | BLACK casting |
|---|---|
| External business email | 15-year B2B SaaS senior, Bain-consultant reply tone |
| Executive PPT | 17-year strategy director, McKinsey/Bain exec-deck tone |
| Crisis apology | 18-year crisis-comms director, PR triage tone |
| Landing page | 17-year growth marketer & landing UX copywriter, Silicon Valley SaaS tone |

The four critics shift the same way. The vocabulary RED uses for an email is not the
vocabulary RED uses for an IR earnings call.

### 2. GOLD is a reader, not a critic

RED, SILVER, and BLUE evaluate the draft. **GOLD does not.** GOLD simulates the actual
recipient *in a specific scene*:

> "Tuesday 9am, the CEO scans the deck for 5 minutes right before the exec meeting."

GOLD asks "will this person sign / ask a follow-up / close the tab?", not "is this good?"
That scene-based reader simulation is the most distinctive piece of the harness.

### 3. Critics disagree on purpose

If the score spread σ ≥ 0.5, debate is triggered automatically. The highest and lowest scorer
exchange short comments and re-score. Consensus is never forced. Most harnesses average and
move on; 5-Color averages *only when agreement is cheap*, and surfaces the disagreement when
it isn't.

### 4. A real numeric pass bar

Not "good enough." A 3-reviewer average ≥ 9.5 **and** GOLD engagement ≥ 9.5. If the bar isn't
met after 4 rounds, the engine forces output and reports: "below 9.5 (max=9.2). Possible
casting or task-definition issue. 1-on-1 recommended." The bar's transparency is the value.

### 5. Pre-critique anti-pattern correction

Five detectors run *before* the four critics ever see the draft:

| Detector | Catches |
|---|---|
| `VAGUE_CTA` | Emails ending in "please review" with no clear verb |
| `LEGAL_RISK_TERM` | Absolute promises ("guarantee," "100%") in legal/external comms |
| `HALLUCINATED_NUMBER` | Unsourced percentages or counts |
| `MISSING_GOLD_HOOK` | First 200 chars don't activate the GOLD scene |
| `TONE_MISMATCH` | First sentence vocabulary drifts from cast tone |

BLACK rewrites itself before review; the round counter is not decremented. Three consecutive
hits on the same pattern escalate to the user. Critics never waste cycles on first-order
defects.

### 6. The case library is the asset

`/roasting` is not a generic writing assistant. Each of the 68 cases ships with its own:
BLACK casting, RGSB persona definitions, GOLD scene, pass-line criteria, forbidden phrases,
and style rules. The asset is *which experts to cast for which artifact*, captured as
checked-in `.md` files at `skills/roasting/references/cases/p*.md` and mirrored on the
canonical [5color site](https://airoasting.github.io/5color).

---

## How it differs from other harness patterns

| Pattern | Typical shape | 5-Color Harness |
|---|---|---|
| **Director-Critic** | 1 generator + 1 critic | 4 critics on *different axes*, debate when σ ≥ 0.5 |
| **Self-Refine / CoT** | One model talking to itself | 5 *cast* personas with role-bleed prohibition |
| **Multi-Agent Debate** | 2-3 homogeneous agents arguing | 4 heterogeneous axes (logic / domain / empathy / reader scene) |
| **Constitutional AI** | Rule-based self-critique | Persona-and-scene-based critique tied to a specific case |
| **Generic Producer-Reviewer** | 1+1, average or pass/fail | 1+4, 9.5 bar, 4-round cap, pre-critique anti-pattern loop |
| **RLHF / RLAIF** | Training-time feedback | Inference-time inline critique, per user call |

The core distinction: most harnesses use a *general-purpose evaluator*. 5-Color makes the
*recipient's situation* and the *case-specific professional standards* into the critics'
identity. The question shifts from "is this good?" to "*will this specific reader, in this
specific scene, take the next action?*"

The second distinction: critique happens in two layers. Anti-pattern detectors clean
first-order defects before the human-modeled critics arrive. Critics focus on logic,
structure, tone, and reader engagement. Never on missing citations or vague CTAs.

---

## Quick samples

```
/roasting 거래처 부장한테 8월 12일까지 회신 달라는 메일
→ p1 외부 비즈니스 이메일 → output.md (concise B2B email, 4-reviewer scored)

/roasting 이번 분기 임원 PPT (실적 + 리스크 + 결정사항 3개)
→ p41 임원 PPT → output.html (slide_library template, `slides` mode)

/roasting B2B SaaS 결제 모듈 랜딩페이지
→ p70 웹사이트·랜딩페이지 → output.html (template + landing-section injection, `landing` mode)

/roasting Stripe 스타일 SaaS 한 페이지 사이트 만들어줘
→ p73 웹사이트 제작 → output.html (BLACK writes complete HTML directly, `direct` mode)

/roasting 인스타 릴스 커버 이미지 프롬프트 짜줘
→ p74 이미지 제작 → output.md (7-step prompt set: scene / framing / lighting / palette / style / aspect / negative)

/roasting 삼성전자 분기 실적 1페이지로
→ p75 DART-based company analysis (auto-enriched via /dart) → output.md
```

### What the output actually looks like

Input:
```
/roasting 거래처 부장한테 8월 12일까지 회신 달라는 메일
```

Polished output (after 4-reviewer pass, scores RED 9.5 / SILVER 9.6 / BLUE 9.4 / GOLD 9.6):
```
김OO 부장님,

지난 협의 건 답변을 8월 12일(월) 18시까지 회신 부탁드립니다.
회신이 늦어지면 다음 본부장 회의 안건 상정이 어려워, 동일 사안을
9월로 이연해야 합니다.

답변이 어려운 경우 일정 조정도 가능합니다. 한 줄로 알려주십시오.

[발신자 / 직책 / 회사]
```

If the engine fails to reach 9.5 after round 4, it forces output and reports honestly:
```
Done. Below 9.5 (max=9.2, round 4 forced output).
Likely cause: BLUE 8.9. Deadline pressure too direct for the recipient's expected register.
Next action: revisit casting or task framing. 1-on-1 recommended.
```

The bar's transparency is the value. Failed runs surface the gap rather than passing
under-quality work.

### Why 9.5 and not 9.0 or 9.7?

The bar is not uniform across cases. Defect weight differs per artifact type.

| Bar | Applies to | Why |
|---|---|---|
| **9.0** | Personal-tone assets (poetry, fiction, personal blog) | No single answer exists. Quantitative pressure flattens the author's voice. |
| **9.5** (default) | Standard white-collar artifacts (emails, reports, internal comms) | Beta data shows ≥ 9.5 yields > 90% of recipients taking the intended next action. |
| **9.7** | Defect-as-loss artifacts (contracts, board memos, shareholder letters, apologies, IR) | A single absolute-promise word creates legal exposure; one shifted phrase loses trust. |

The bar is declared in the case definition's BLACK-casting line, alongside word count and
end-of-sentence style.

---

## Three deliverables per call

| File | Content | Use |
|---|---|---|
| `output.{md|html}` | Final artifact | What the executive actually uses |
| `critique.md` | Per-round reviewer comments | Teaching material, next-call learning |
| `reasoning.md` | BLACK decision log + anti-pattern history | Audit, reproducibility, debugging |

All three live in `~/.claude/roasting/_workspace/{session}/final/`. Nothing leaves the local
machine.

---

## Korean cases, universal pattern

The 68 case definitions, critic personas, and quality rules are written in Korean and built
for Korean white-collar workflows. English input falls back to general 5-Color mode without
case-specific seeds.

The underlying *harness pattern* is language-agnostic: per-case persona casting, mandatory
debate when score spread σ ≥ 0.5, a 9.0 / 9.5 / 9.7 tiered pass bar, pre-critique
anti-pattern correction, and a scene-cast GOLD reader. If you want to build the same kind
of execution engine in another language or domain, this repository is a reference
architecture. For Korean-language details see [README.ko.md](README.ko.md).

---

## Privacy

Telemetry, if enabled, contains metadata only: case ID, round count, score distribution,
detected anti-patterns, completion status. **No user input (`xxxxx`), no draft content, no
critic comments ever leave the local machine.** Outputs and reasoning logs live entirely in
`~/.claude/roasting/_workspace/`.

---

## Cost

Roughly **~$0.36 per call** at default settings: 5 personas × 4-round cap × fixed case
definitions. Cost is deterministic, not exploratory.

---

## Status

**Open Beta v0.4.1.** Production-ready for individual use. The Agent Teams path remains
experimental and falls back to sequential sub-agent execution on error. Known limits and
roadmap are in [README.ko.md § 12 알려진 한계](README.ko.md).

### What's new in v0.4 (2026-05-17)

- **Fallback workflow enforced.** Even when the case library doesn't match, BLACK + RGSB
  4-reviewer scoring + 9.5 gate run end-to-end with a generic 5-persona profile. No
  shortcutting.
- **`assisted` builder mode added.** HTML builder now has 4 modes: `slides` / `landing` /
  `direct` / `assisted`. The new mode handles generic-case + HTML requests by picking one of
  the 35 `slide_library` templates as the base, then letting BLACK inject content + any
  needed interactions (tabs, filters, etc.).
- **`html_mode` frontmatter field.** Case files now declare their HTML mode explicitly.
  SKILL.md no longer hardcodes case IDs.
- **taste-skill integration.** 8 design-related cases (p41/42/43/45/p59/p70/p73/p74) plus
  generic-case + HTML now auto-enrich with [Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill)
  variants (`design-taste-frontend`, `brandkit`, `imagegen-frontend-web`, etc.) for
  anti-slop output. Install: `npx skills add https://github.com/Leonxlnx/taste-skill`.
  Graceful degradation if not installed.
- **Real enrich dispatch.** `/dart`, `/strategy`, and taste-skill variants are now invoked
  through Claude's `Skill` tool directly. The earlier stub references to non-existent Python
  scripts have been replaced with explicit "Claude procedure" descriptions.

Verified quality metrics (v0.2 measurement; no regression in v0.3 / v0.4 / v0.4.1):

| Gate | Target | Measured |
|---|---|---|
| Routing top-1 accuracy | ≥ 90% (Wilson 95% LB) | **98.4%** (LB 0.954) on 204 phrasings |
| Anti-pattern false positive | 0% | **0%** (50 / 50) |
| Unit + integration tests | green | **102 / 102 pass** |
| Quality-gate scenarios (avg) | ≥ 9.0 | **9.17** (1 / 18 sampled; full run planned for v0.5) |

---

## Architecture (one paragraph)

7-phase pipeline. **Phase 0** initializes a session workspace. **Phase 1** routes against
the 68-case index; if all candidates score below 0.5 confidence, it falls back to
`generic_case` mode with a generic 5-persona profile (BLACK + RGSB + 9.5 gate still
enforced). **Phase 2** loads the case definition, reads the `html_mode` frontmatter field
(`slides` / `landing` / `direct` / `assisted`) to pick a `slide_library` template for
non-`direct` HTML cases, and optionally invokes adjacent skills (`/dart`, `/strategy`,
taste-skill variants) declared in the case's `enrich:` field. **Phase 3** runs BLACK to
produce a first draft. **Phase 4** runs five anti-pattern detectors with a 3-strike cap.
**Phase 5** runs RGSB review (Agent Teams primary path: 4 critics in parallel, with
`SendMessage` debate; sub-agent fallback if `TeamCreate` is unavailable). **Phase 6** loops
back to Phase 3 if the average is below 9.5 and round count < 4. **Phase 7** delivers the
three artifacts.

Details: [skills/roasting/SKILL.md](skills/roasting/SKILL.md).

---

## Contributing

Bug reports and feedback are welcome via GitHub Issues. From inside Claude:

```
/roasting --feedback
```

This opens a pre-filled GitHub Issue with session metadata attached. **Content is never
included.** The issue contains case ID, round count, completion status, and your own free
text. No drafts, no critic comments, no user input.

---

## License

MIT. See [LICENSE](LICENSE).
