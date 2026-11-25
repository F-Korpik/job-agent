import pytest

from job_agent.mail_types import classify, load_mail_rules

RULES = load_mail_rules()


@pytest.mark.parametrize("sender, subject, expected", [
    ('"Wyszukiwane w Pracuj.pl" <jobalert@wysylka.pracuj.pl>', "Oferty na które czekasz - 20.11.2026 - Poznań", "pracuj_alert"),
    ('"Pracuj.pl" <rekomendacje@wysylka.pracuj.pl>', "Business Planning Analyst - oferta 17.11.2026", "pracuj_rekomendacje"),
    ("No Fluff Jobs <notifications@nofluffjobs.com>", "\tNowe oferty pracy, 7 dopasowane do Twoich kryteriów", "nfj_alert"),
    ("No Fluff Jobs <notifications@nofluffjobs.com>", "Nowy tydzień, nowa praca – sprawdź oferty", "nfj_inne"),
    ("No Fluff Jobs <notifications@nofluffjobs.com>", "Najlepsze oferty pracy z ostatniego tygodnia", "nfj_inne"),
    ('"justjoin.it" <jobs@hello.justjoin.it>', "Proponowane oferty - justjoin.it", "jjit_proponowane"),
    ("Ktoś <ktos@example.com>", "You applied for Data Engineer", "nieznany"),
])
def test_classify(sender, subject, expected):
    assert classify(sender, subject, RULES).name == expected


def test_unknown_mail_is_skipped():
    assert classify("x@example.com", "cokolwiek", RULES).process is False


def test_every_rule_is_complete():
    for rule in RULES:
        assert {"name", "sender", "process"} <= rule.keys()
        assert isinstance(rule["process"], bool)