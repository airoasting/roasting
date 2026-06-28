# Roasting · 에이전트 팀 빌더 (실행 엔진)

![Version](https://img.shields.io/badge/Version-1.0.0-2ea44f)
![License](https://img.shields.io/badge/License-Apache%202.0-1f6feb)
![Claude Code](https://img.shields.io/badge/Claude%20Code-Skill-8957e6)
![Agents](https://img.shields.io/badge/Agents-50%20Verified-d2691e)
![Recipes](https://img.shields.io/badge/Recipes-12%20Harnesses-d2691e)
![Mode](https://img.shields.io/badge/Mode-Agent%20Teams-2ea44f)
![Native](https://img.shields.io/badge/Native-Claude%20Code-8957e6)
![Also on](https://img.shields.io/badge/Also%20on-ChatGPT-555555)

> 목적 한 줄을 받아, 검증된 50명 에이전트 팀원 중에서 팀을 설계하고 **실제로 돌려** 검토 통과본까지 만들어 내는 Claude Code 스킬.

`AI ROASTING`이 로스팅(5색 다관점 채점)으로 검증한 50개 역할 프롬프트와 12개 검증된 팀 레시피를 기반으로, 사용자가 "무엇을 만들지(목적)"만 말하면 팀장(오케스트레이터)이 "누가 어떤 순서로 하는지"를 정하고 끝까지 진행한다.

**기본(네이티브) 플랫폼은 Claude Code다.** 독립 에이전트로 팀을 돌리고 검토자도 진짜 독립이라 9.5 게이트가 가장 강하게 작동한다. [ChatGPT는 호환 모드로도 쓸 수 있다](#chatgpt에서-쓰기)(단일 모델 순차 실행).

## 무엇을 하나

목적 입력 → ① 목적 파악 → ② 팀 설계 → ③ 팀 구조 제시 → ④ 실행 → ⑤ 검토(9.5 게이트) → 최종 결과.

- **부품(Agent)** 50개 = 단일 역할 시스템 프롬프트. 전부 9.5+ 합격선으로 로스팅 검증.
- **레시피(Harness)** 12개 = 부품을 handoff로 엮은 검증된 팀(리서치 보고서·시장 분석·재무 리뷰·발표자료·전략·회의 정리 등).
- **라우터** = 목적 → 레시피 매칭 또는 부품 새 조합. 이게 핵심 IP다.

## 설치

```bash
# 프로젝트의 .claude/skills/ 아래로 복사
cp -r roasting <your-project>/.claude/skills/roasting
```

Claude Code를 재시작하면 스킬이 로드된다.

## 사용법

```
/roasting 경쟁사 3곳을 분석해서 이사회용 보고서 만들어줘
```

또는 "팀 짜줘", "이거 팀으로 해줘", 혹은 보고서·분석·발표자료·제안서·재무검토·회의정리 같은 결과물을 "만들어 달라"고 하면 발동한다. 어떤 팀원이 필요한지 몰라도 목적만 주면 된다.

## 실행 모드 (티어드)

쓸 수 있는 도구에 따라 위에서부터 고른다.

1. **에이전트 팀**: `TeamCreate`/`SendMessage`/`TaskCreate` 가능 시. 팀원이 공유 작업목록으로 자체 조율.
2. **서브에이전트**: `Agent` 도구만 있으면. 의존 단계는 파이프라인, 독립 단계는 병렬(fan-out). (기본·안정)
3. **순차 역할극**: 에이전트 도구가 없으면 팀장이 직접 역할을 순서대로 수행. (폴백)

핵심은 팀원이 **각자 독립 컨텍스트**라는 점이다. 그래서 (a) 검토자가 진짜 독립이라 9.5 게이트가 자기채점이 아니고, (b) 독립 단계를 병렬로 돌린다.

## 품질 게이트

검토자는 산출물을 만들지 않은 **독립 에이전트**로, 사용자의 원래 목적·자료에 대고 구체적 결함부터 찾는다. 결함이 하나라도 있으면 9.5를 주지 않고, 그 단계로 한 번 되돌려 보강한 뒤 통과시킨다. (실측 테스트에서 게이트가 첫 통과를 거부하고 6.5로 불합격 처리한 뒤 보강을 요구했다. 통과를 거저 주지 않는, 실제로 떨어지는 게이트다.)

## 실행 결과 (워크스페이스)

Claude Code에서 실행하면, 그 실행의 팀과 산출물이 파일로 남는다.

```
_workspace/
└── 20260628_01/             # {YYYYMMDD}_NN, 같은 날 재호출 시 _02·_03
    ├── team.md              # 빌드 시트: 목적·팀 구조·순서·토글
    ├── lead/                # 팀장(오케스트레이터)
    │   └── lead.md
    ├── agents/              # 배치된 팀원(역할 프롬프트 + 이번 io)
    │   ├── 1-research-assistant.md
    │   ├── 2-summarizer.md
    │   └── review-copy-editor.md
    └── output/              # 단계별 산출물 + 최종결과.md
```

팀이 일회성으로 사라지지 않고 자산으로 남아, 다시 보거나 재사용할 수 있다. (ChatGPT 호환 모드는 파일시스템이 없어 팀·산출물을 화면 인라인으로만 보여 준다.)

## ChatGPT에서 쓰기 (호환 모드)

기본은 Claude Code지만, **ChatGPT(Custom GPT)** 로도 같은 동작을 쓸 수 있다. `platforms/chatgpt/`에 셋업이 있다.

- `platforms/chatgpt/INSTRUCTIONS.md` — Custom GPT "Instructions"에 붙여 넣을 본문
- `platforms/chatgpt/SETUP.md` — 5분 셋업(Instructions 붙여넣기 + `references/` 4개를 Knowledge로 업로드 + 브라우징 켜기)

ChatGPT엔 서브에이전트가 없어 실행은 **단일 모델 순차 모드**(스킬의 폴백 모드)로, 게이트는 "냉정 재독" 독립 검토로 동작한다. 검증된 50 부품·12 레시피·9.5 게이트는 동일하다.

## 장착 도구

일부 팀원은 AI ROASTING 자사 도구를 역할별로 쥐고 있다.

| 도구 | 용도 | 받는 팀원 |
|---|---|---|
| [전략 도구 갤러리](https://airoasting-strategy.vercel.app/) | 70개 컨설팅 프레임워크 | 전략 기획·SWOT·비즈니스 케이스·의사결정 |
| [5color](https://5color.vercel.app/) | 5인 페르소나 검토 지침 생성 | 품질 검수·비판적 검토·문서 검토·교정 |
| [슬라이드 라이브러리](https://airoasting-slide.vercel.app/) | 35개 HTML 슬라이드 템플릿 | 프레젠테이션 기획·제안서 |
| [AI ROASTING 블로그](https://airoasting-blog.vercel.app/) | 글로벌 리서치 인사이트 | 리서치·트렌드·마켓 |
| [스킬 라이브러리](https://airoasting-skill.vercel.app/) | 엄선된 실무 AI 스킬 | 자동화 설계·SOP |

## 구조

```
roasting/
├── SKILL.md                       # 트리거 · 설계 알고리즘 · 실행 프로토콜 · 9.5 게이트
├── README.md                      # 이 문서
├── LICENSE                        # Apache License 2.0
├── references/
│   ├── catalog.md                 # 50명 부품 표(선발용)
│   ├── harnesses.md               # 12 레시피 + 토글 + 매칭 키워드
│   ├── agent-prompts.md           # 50명 전체 시스템 프롬프트(실행용, id로 선택)
│   └── execution-modes.md         # 실행 모드 3종 · 병렬/순차 · 에이전트·검토자 템플릿
└── platforms/
    └── chatgpt/
        ├── INSTRUCTIONS.md        # Custom GPT Instructions 본문
        └── SETUP.md               # ChatGPT 셋업 가이드
```

## 라이선스

Copyright 2026 AI ROASTING (Jayden Kang). [Apache License 2.0](./LICENSE) 하에 배포된다.
