from dataclasses import dataclass, field
from datetime import date

from .sheets import mail_row


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