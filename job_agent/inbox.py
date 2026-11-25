from dataclasses import dataclass, field
from datetime import date

from .sheets import mail_row
from .mail_text import message_text
from .mail_types import classify


@dataclass
class MailResult:
    message_id: str
    subject: str
    mail_type: str
    rows: list[list] = field(default_factory=list)
    error: str | None = None


def process_mails(mails: list[dict], handle) -> list[MailResult]:
    results = []
    for mail in mails:
        try:
            results.append(handle(mail))
        except Exception as e:
            results.append(MailResult(mail["id"], mail.get("subject", ""), mail.get("type", "?"),
                                      error=f"{type(e).__name__}: {e}"))
    return results


def processed_mail_rows(results: list[MailResult], today: date) -> list[list]:
    return [mail_row(r.message_id, r.mail_type, r.subject, len(r.rows), today)
            for r in results if r.error is None]


def gmail_query(days: int, label: str = "oferty") -> str:
    if days < 1:
        raise ValueError("days musi być co najmniej 1")
    return f"label:{label} newer_than:{days}d"


def get_header(payload: dict, name: str) -> str:
    for header in payload.get("headers", []):
        if header["name"].lower() == name.lower():
            return header["value"]
    return ""


def make_handler(fetch, mail_rules: list[dict], process):
    def handle(mail: dict) -> MailResult:
        payload = fetch(mail["id"])["payload"]
        subject = get_header(payload, "Subject")
        mail_type = classify(get_header(payload, "From"), subject, mail_rules)
        if not mail_type.process:
            return MailResult(mail["id"], subject, mail_type.name)
        rows = process(message_text(payload))
        return MailResult(mail["id"], subject, mail_type.name, rows=rows)
    return handle