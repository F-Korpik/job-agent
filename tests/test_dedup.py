from job_agent.dedup import deduplicate, offer_key
from job_agent.models import Offer


def make(company: str, title: str, **kwargs) -> Offer:
    return Offer(company=company, title=title, **kwargs)


def test_same_company_and_title_are_duplicates():
    offers = [
        make("FarmaProm", "Analytics Engineer", url="https://a"),
        make("FarmaProm", "Analytics Engineer", url="https://b"),
    ]
    assert len(deduplicate(offers)) == 1


def test_case_and_whitespace_are_ignored():
    assert offer_key(make("FarmaProm", "Analytics  Engineer ")) == offer_key(make("farmaprom", "analytics engineer"))


def test_different_titles_are_kept():
    offers = [
        make("FarmaProm", "Analytics Engineer"),
        make("FarmaProm", "Specjalista ds. inżynierii analitycznej"),
    ]
    assert len(deduplicate(offers)) == 2


def test_keeps_first_occurrence_in_order():
    offers = [
        make("A", "X", url="https://first"),
        make("B", "Y"),
        make("A", "X", url="https://second"),
    ]
    result = deduplicate(offers)
    assert [o.company for o in result] == ["A", "B"]
    assert result[0].url == "https://first"