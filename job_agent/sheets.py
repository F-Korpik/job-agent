import os
from datetime import date

import gspread
from dotenv import load_dotenv

from .dedup import offer_key
from .models import Offer, Score
from .triage import TriageResult

load_dotenv()

HEADERS = [
    "offer_id", "dodano", "decyzja", "wynik", "kierunek", "firma", "tytul",
    "lokalizacja", "tryb", "umowa", "widelki", "uzasadnienie", "braki",
    "red_flags", "powody_flagi", "pewna_firma", "tagi", "url", "portal",
]


def _salary(offer: Offer) -> str:
    if offer.salary_min is None and offer.salary_max is None:
        return ""
    return f"{offer.salary_min}–{offer.salary_max} {offer.currency or ''} {offer.salary_period or ''}".strip()


def offer_to_row(offer: Offer, result: TriageResult, score: Score | None, today: date) -> list:
    if result.decision == "reject":
        decision = "odrzucona"
    elif score is None:
        decision = "błąd oceny"
    else:
        decision = "do przejrzenia"
    return [
        offer_key(offer),
        today.isoformat(),
        decision,
        score.score if score else "",
        score.direction if score else "",
        offer.company,
        offer.title,
        offer.location or "",
        offer.work_mode or "",
        ", ".join(offer.contract_types),
        _salary(offer),
        score.summary if score else "",
        ", ".join(score.gaps) if score else "",
        ", ".join(score.red_flags) if score else "",
        "; ".join(result.reasons or result.flags),
        {True: "tak", False: "nie"}.get(offer.grounded, ""),
        ", ".join(offer.tags),
        offer.url or "",
        offer.portal,
    ]


def select_new(rows: list[list], existing_ids: list[str]) -> list[list]:
    seen = set(existing_ids)
    new = []
    for row in rows:
        if row[0] not in seen:
            new.append(row)
            seen.add(row[0])
    return new


def open_worksheet():
    client = gspread.service_account(filename=os.environ["GOOGLE_CREDENTIALS_FILE"])
    ws = client.open_by_key(os.environ["SHEET_ID"]).worksheet("oferty")
    header = ws.row_values(1)
    if not header:
        ws.append_row(HEADERS)
    elif header != HEADERS:
        raise ValueError(f"Nagłówki w zakładce 'oferty' różnią się od oczekiwanych: {header}")
    return ws
    

def append_new(ws, rows: list[list]) -> tuple[int, int]:
    existing_ids = ws.col_values(1)[1:]
    new = select_new(rows, existing_ids)
    if new:
        ws.append_rows(new, value_input_option="RAW")
    return len(new), len(rows) - len(new)