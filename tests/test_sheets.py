from datetime import date

from job_agent.models import Offer, Score
from job_agent.sheets import HEADERS, offer_to_row, select_new
from job_agent.triage import TriageResult

TODAY = date(2026, 11, 22)
OFFER = Offer(company="FarmaProm", title="Analytics Engineer", contract_types=["UoP"], grounded=True)


def test_row_matches_headers():
    row = offer_to_row(OFFER, TriageResult("pass"), None, TODAY)
    assert len(row) == len(HEADERS)


def test_rejected_offer_has_reason_and_no_score():
    row = dict(zip(HEADERS, offer_to_row(OFFER, TriageResult("reject", ["tylko B2B"]), None, TODAY)))
    assert row["decyzja"] == "odrzucona"
    assert row["wynik"] == ""
    assert row["powody_flagi"] == "tylko B2B"


def test_scored_offer():
    score = Score(score=78, direction="docelowy", summary="Pasuje.", gaps=["BigQuery"])
    row = dict(zip(HEADERS, offer_to_row(OFFER, TriageResult("pass"), score, TODAY)))
    assert row["decyzja"] == "do przejrzenia"
    assert row["wynik"] == 78
    assert row["kierunek"] == "docelowy"
    assert row["braki"] == "BigQuery"
    assert row["pewna_firma"] == "tak"


def test_select_new_skips_existing_and_repeats():
    rows = [["a", 1], ["b", 2], ["a", 3], ["c", 4]]
    assert select_new(rows, existing_ids=["b"]) == [["a", 1], ["c", 4]]