from scripts.anti_patterns import _hallucinated_number


def test_detects_unsourced_pct(fake_judge):
    judge = fake_judge({"unsourced_numbers": ["23%"]})
    result = _hallucinated_number(
        text="이번 분기 매출 23% 성장.",
        case_id="c23",
        user_xxxxx="분기 보고서",
        judge=judge,
    )
    assert result is not None
    assert result.name == "HALLUCINATED_NUMBER"
    assert "23%" in result.detail


def test_detects_unsourced_amount(fake_judge):
    judge = fake_judge({"unsourced_numbers": ["120억"]})
    result = _hallucinated_number(
        "이번 라운드는 120억 규모이다.", "c34", "투자 메모", judge,
    )
    assert result is not None


def test_detects_user_count(fake_judge):
    judge = fake_judge({"unsourced_numbers": ["340만 명"]})
    result = _hallucinated_number(
        "월 활성 사용자 340만 명.", "c23", "분석 보고서", judge,
    )
    assert result is not None


def test_detects_growth_multiple(fake_judge):
    judge = fake_judge({"unsourced_numbers": ["3.2배"]})
    result = _hallucinated_number(
        "전년 대비 3.2배 성장.", "c23", "성과 리뷰", judge,
    )
    assert result is not None


def test_detects_dollar_amount(fake_judge):
    judge = fake_judge({"unsourced_numbers": ["$5M"]})
    result = _hallucinated_number(
        "Series A $5M 라운드를 종료했다.", "c34", "IC memo", judge,
    )
    assert result is not None


# --- Negative cases (must NOT detect) ---

def test_no_numbers_clean(fake_judge):
    judge = fake_judge({"unsourced_numbers": []})
    assert _hallucinated_number("이번 분기는 잘 풀렸다.", "c23", "보고", judge) is None


def test_sourced_numbers_clean(fake_judge):
    judge = fake_judge({"unsourced_numbers": []})
    assert _hallucinated_number(
        "이번 분기 매출 23% [출처: 사내 ERP].",
        "c23", "분기 보고서", judge,
    ) is None


def test_exempt_poem_p64(fake_judge):
    judge = fake_judge({"unsourced_numbers": ["천 번"]})
    # case c64 = 시 — 면제 카테고리.
    assert _hallucinated_number(
        "천 번을 부르고 만 번을 외쳐도",
        "c64", "시", judge,
    ) is None


def test_exempt_novel_p63(fake_judge):
    judge = fake_judge({"unsourced_numbers": ["1942"]})
    assert _hallucinated_number(
        "그는 1942년에 태어났다.",
        "c63", "소설", judge,
    ) is None


def test_exempt_linkedin_profile_p69(fake_judge):
    judge = fake_judge({"unsourced_numbers": ["10년"]})
    assert _hallucinated_number(
        "10년차 시니어 PM",
        "c69", "프로필", judge,
    ) is None
