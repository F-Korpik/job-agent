from job_agent.evaluate import compare
from job_agent.models import Offer

EXPECTED = [("Momentum", "Machine Learning Engineer"), ("G2A", "AI Automation Engineer")]


def offer(company: str, title: str) -> Offer:
    return Offer(company=company, title=title)


def test_all_correct():
    r = compare(EXPECTED, [offer("Momentum", "Machine Learning Engineer"), offer("G2A", "AI Automation Engineer")])
    assert len(r.correct) == 2
    assert r.recall == 1.0 and r.precision == 1.0


def test_case_differences_still_correct():
    r = compare(EXPECTED, [offer("momentum", "machine learning  engineer")])
    assert len(r.correct) == 1


def test_wrong_company_is_not_also_missing():
    r = compare(EXPECTED, [offer("Sii", "Machine Learning Engineer"), offer("G2A", "AI Automation Engineer")])
    assert len(r.wrong_company) == 1
    assert r.missing == []
    assert r.precision == 0.5


def test_missing_offer():
    r = compare(EXPECTED, [offer("G2A", "AI Automation Engineer")])
    assert r.missing == [("Momentum", "Machine Learning Engineer")]
    assert r.recall == 0.5


def test_extra_offer():
    r = compare(EXPECTED, [offer("G2A", "AI Automation Engineer"), offer("Acme", "Mamy dla Ciebie dobre wieści")])
    assert r.extra == [("Acme", "Mamy dla Ciebie dobre wieści")]