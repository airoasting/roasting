# /roasting Workflow Rules

## 합격선

- 분석가 3인(RED, SILVER, BLUE) 평균 ≥ 9.5
- GOLD 별도 보고 (타이브레이커 1순위)
- 4라운드 권장 cap

## 점수 기준

- 10 = 결함 없음
- 9.5 = 합격선
- 9 = 한 자리 더 손보면
- 8 = v2 권장
- ≤ 7 = 캐스팅/과제 정의 의심

## 발화 톤

각 페르소나는 케이스 정의에 명시된 톤을 그대로 사용. 전체 풀:
건조 · 단정 · 신랄 · 차분 · 깐깐 · 냉정 · 회의적 · 무뚝뚝 · 속내 드러냄 · 실무자 직설.

세 비평가 톤이 서로 달라야 한다.

## _workspace 컨벤션

```
~/.claude/roasting/_workspace/{YYYYMMDD-HHMMSS}-{tmp_id}/
├── input.txt                 # xxxxx
├── routing.json              # Phase 1 결과
├── case-context.json         # Phase 2 결과
├── round-1/
│   ├── black-draft.{md|html}
│   ├── anti-patterns.json
│   ├── rgsb-scores.json
│   └── debate-log.md
├── round-2/...
└── final/
    ├── output.{html|md}
    ├── critique.md
    └── reasoning.md
```

## 토론 트리거 룰

- σ ≥ 0.5 → 토론 1라운드.
- 가장 높은 점수 페르소나 ↔ 가장 낮은 점수 페르소나.
- **타이브레이커**: 점수 동률 시 GOLD > RED > SILVER > BLUE.
- 1라운드 후 σ 여전히 ≥ 0.5 → "합의 실패" 표시 + 분포 그대로 출력.

## 라운드 cap

- 4라운드 후 < 9.5 → 가장 높았던 라운드 결과 사용 + 사용자 보고: "9.5 미달 (max=X.Y). 캐스팅 또는 과제 정의 문제 가능성. 1on1 권장."

## 3-strikes 안티패턴 보호

- 동일 안티패턴 3회 연속 검출 (한 라운드 내 OR 라운드 간 누적) → 사용자 보고:
  - (1) 진행 (강제 통과)
  - (2) 중단
  - (3) 케이스 재선택
