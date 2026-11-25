import base64

from datetime import date

from job_agent.inbox import MailResult, process_mails, processed_mail_rows
from job_agent.inbox import make_handler
from job_agent.mail_types import load_mail_rules

TODAY = date(2026, 11, 25)
MAILS = [
    {"id": "a", "subject": "Alert 1", "type": "nfj_alert"},
    {"id": "b", "subject": "Alert 2", "type": "pracuj_alert"},
    {"id": "c", "subject": "Alert 3", "type": "nfj_alert"},
]


def fake_handle(mail):
    if mail["id"] == "b":
        raise ValueError("model zwrócił śmieci")
    return MailResult(mail["id"], mail["subject"], mail["type"], rows=[["oferta"]])


def test_one_failing_mail_does_not_stop_others():
    results = process_mails(MAILS, fake_handle)
    assert [r.message_id for r in results] == ["a", "b", "c"]
    assert results[1].error == "ValueError: model zwrócił śmieci"
    assert results[1].rows == []


def test_failed_mail_is_not_marked_processed():
    results = process_mails(MAILS, fake_handle)
    rows = processed_mail_rows(results, TODAY)
    assert [row[0] for row in rows] == ["a", "c"]


def test_skipped_mail_is_marked_processed_with_zero_offers():
    results = [MailResult("x", "Reklama", "nfj_inne")]
    assert processed_mail_rows(results, TODAY)[0][4] == 0


import pytest

from job_agent.inbox import gmail_query, get_header


def test_gmail_query():
    assert gmail_query(3) == "label:oferty newer_than:3d"


def test_gmail_query_rejects_zero_days():
    with pytest.raises(ValueError):
        gmail_query(0)


def test_get_header_is_case_insensitive_and_defaults_to_empty():
    payload = {"headers": [{"name": "Subject", "value": "Nowe oferty"}]}
    assert get_header(payload, "subject") == "Nowe oferty"
    assert get_header(payload, "From") == ""


def fake_message(sender, subject, text):
    data = base64.urlsafe_b64encode(text.encode()).decode()
    return {"payload": {"mimeType": "text/plain", "body": {"data": data},
                        "headers": [{"name": "From", "value": sender}, {"name": "Subject", "value": subject}]}}


def test_handler_processes_alert():
    seen = []
    msg = fake_message("No Fluff Jobs <notifications@nofluffjobs.com>", "Nowe oferty pracy, 2", "Data Engineer")
    handle = make_handler(lambda _id: msg, load_mail_rules(), lambda text: seen.append(text) or [["row"]])
    result = handle({"id": "m1"})
    assert result.mail_type == "nfj_alert" and result.rows == [["row"]]
    assert seen == ["Data Engineer"]


def test_handler_skips_recommendations_without_calling_model():
    msg = fake_message("Pracuj.pl <rekomendacje@wysylka.pracuj.pl>", "Oferta", "cokolwiek")
    handle = make_handler(lambda _id: msg, load_mail_rules(), lambda text: 1 / 0)
    result = handle({"id": "m2"})
    assert result.mail_type == "pracuj_rekomendacje" and result.rows == []