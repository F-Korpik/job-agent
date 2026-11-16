import csv
from pathlib import Path

from job_agent.models import Offer
from job_agent.triage import matches_rule
from job_agent.triage import load_rules, matches_rule, triage

TITLE_RULE = {"reason": "test", "fields": ["title"], "words": ["Data Analyst", "Lead"]}
TAG_RULE = {"reason": "test", "fields": ["tags"], "words": ["SAP"]}

LABELS = Path(__file__).parent / "eval" / "triage_labels.csv"
PERIODS = {"miesiąc": "month", "rok": "year", "godzina": "hour", "": None}


def offer(title: str, tags: list[str] | None = None) -> Offer:
    return Offer(company="X", title=title, tags=tags or [])


def test_word_in_title():
    assert matches_rule(offer("Senior Data Analyst"), TITLE_RULE)


def test_case_insensitive():
    assert matches_rule(offer("data analyst"), TITLE_RULE)


def test_whole_word_only():
    assert not matches_rule(offer("Leading Data Engineer"), TITLE_RULE)


def test_field_outside_rule_is_ignored():
    assert not matches_rule(offer("Data Engineer", tags=["Data Analyst"]), TITLE_RULE)


def test_word_in_tags():
    assert matches_rule(offer("Data Engineer", tags=["Python", "SAP"]), TAG_RULE)


def test_phrase_does_not_span_two_tags():
    assert not matches_rule(offer("X", tags=["Data", "Analyst"]), {**TITLE_RULE, "fields": ["tags"]})


def _int_or_none(value: str) -> int | None:
    return int(value) if value else None


def label_offers():
    with LABELS.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            yield row, Offer(
                company=row["firma"],
                title=row["tytul"],
                contract_types=row["umowa"].split(";") if row["umowa"] else [],
                salary_min=_int_or_none(row["widelki_min"]),
                salary_max=_int_or_none(row["widelki_max"]),
                salary_period=PERIODS[row["okres"]],
                tags=row["tagi"].split(";") if row["tagi"] else [],
            )


def test_all_good_offers_pass():
    rules = load_rules()
    rejected = [f"{row['firma']} – {row['tytul']}: {triage(o, rules).reasons}"
                for row, o in label_offers()
                if row["decyzja"] == "dobra" and triage(o, rules).decision == "reject"]
    assert rejected == []


def test_most_bad_offers_rejected():
    rules = load_rules()
    bad = [o for row, o in label_offers() if row["decyzja"] == "zla"]
    assert sum(triage(o, rules).decision == "reject" for o in bad) >= 18


def test_b2b_only_rejected():
    assert triage(Offer(company="X", title="Data Engineer", contract_types=["B2B"]), load_rules()).decision == "reject"


def test_yearly_salary_not_compared_to_monthly_threshold():
    o = Offer(company="X", title="AI Engineer", contract_types=["UoP"], salary_max=200000, salary_period="year")
    assert triage(o, load_rules()).decision == "pass"


def test_classic_ml_is_flagged_not_rejected():
    result = triage(Offer(company="X", title="ML Engineer", tags=["PyTorch"]), load_rules())
    assert result.decision == "pass" and result.flags