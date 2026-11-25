from datetime import date

from job_agent.inbox import MailResult, process_mails, processed_mail_rows

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