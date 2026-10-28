from app.validate import NOT_FOUND_MESSAGE, numbers_in, validate

PASSAGES = [
    {"title": "IRS Publication 15 (2026)", "page": 2, "text": "The social security wage base limit is $184,500."},
    {"title": "IRS Publication 15 (2026)", "page": 44, "text": "The FUTA tax rate is 6.0% on the first $7,000 of wages."},
    {"title": "IRS Publication 587 (2025)", "page": 10, "text": "The area is limited to 300 square feet at $5 per square foot."},
]


def test_valid_answer_passes_and_is_renumbered():
    r = validate(True, "FUTA is 6.0% of the first $7,000 [2].", [2], PASSAGES)
    assert r.found
    assert r.answer == "FUTA is 6.0% of the first $7,000 [1]."
    assert r.citations == [2]
    assert r.checks["numbers_verified"]


def test_invalid_citation_numbers_are_removed():
    r = validate(True, "The wage base is $184,500 [1][9].", [1, 9], PASSAGES)
    assert r.answer == "The wage base is $184,500 [1]."
    assert r.checks["invalid_citations_removed"] == [9]


def test_found_without_any_valid_citation_is_downgraded():
    r = validate(True, "The wage base is $184,500.", [7], PASSAGES)
    assert not r.found
    assert r.answer == NOT_FOUND_MESSAGE
    assert r.checks["reason"] == "no_valid_citation"


def test_number_not_in_cited_passage_is_flagged():
    # $176,100 appears nowhere in passage 1.
    r = validate(True, "The wage base is $176,100 [1].", [1], PASSAGES)
    assert r.found
    assert not r.checks["numbers_verified"]
    assert r.checks["unverified_numbers"] == ["176100"]


def test_number_must_come_from_a_cited_passage_not_any_passage():
    # 6.0% is in passage 2, but the answer only cites passage 1.
    r = validate(True, "The rate is 6.0% [1].", [1], PASSAGES)
    assert r.checks["unverified_numbers"] == ["6.0"] or r.checks["unverified_numbers"] == ["6"]


def test_years_from_document_title_count_as_verified():
    r = validate(True, "Per Publication 15 (2026), the wage base is $184,500 [1].", [1], PASSAGES)
    assert r.checks["numbers_verified"]


def test_calculated_value_is_flagged_for_review():
    r = validate(True, "The maximum is $1,500 (300 x $5) [3].", [3], PASSAGES)
    assert r.checks["unverified_numbers"] == ["1500"]


def test_partial_answer_keeps_sources():
    r = validate(False, "Only the area limit is covered: 300 square feet [3].", [3], PASSAGES)
    assert not r.found
    assert r.citations == [3]
    assert r.answer.endswith("[1].")
    assert r.checks["reason"] == "partial_answer"


def test_not_found_without_citations():
    r = validate(False, "The documents do not cover this.", [], PASSAGES)
    assert not r.found and r.citations == []
    assert r.checks["reason"] == "model_not_found"


def test_numbers_in_normalises_formatting():
    assert numbers_in("$184,500 and 6.0% and 1.45%") == {"184500", "6", "1.45"}
