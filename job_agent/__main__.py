import argparse
import sys

from datetime import date
from pathlib import Path

from pydantic import ValidationError

from .dedup import deduplicate
from .extract import extract_offers
from .score import build_prompt, load_skills, score_offer
from .sheets import append_new, offer_to_row, open_mail_log, open_worksheet, unprocessed
from .triage import load_rules, triage
from .gmail import get_message, gmail_service, list_messages
from .inbox import gmail_query, make_handler, process_mails, processed_mail_rows
from .mail_types import load_mail_rules



def process_text(text: str, rules: dict, scoring_prompt: str, today: date) -> list[list]:
    offers, errors = extract_offers(text)
    total = len(offers)
    offers = deduplicate(offers)
    width = len(str(len(offers)))
    rows = []
    rejected = 0
    for n, o in enumerate(offers, start=1):
        result = triage(o, rules)
        sal = f"{o.salary_min}-{o.salary_max} {o.currency}" if o.salary_min else "brak widełek"
        if result.decision == "reject":
            rejected += 1
            rows.append(offer_to_row(o, result, None, today))
            print(f"{n:>{width}} ✗   - | {o.company[:22]:22} | {o.title[:45]:45} | {sal:18} | {'; '.join(result.reasons)}")
            continue
        try:
            s = score_offer(o, scoring_prompt)
        except ValidationError as e:
            rows.append(offer_to_row(o, result, None, today))
            print(f"{n:>{width}} ✓   ? | {o.company[:22]:22} | {o.title[:45]:45} | błąd oceny: {e.errors()[0]['msg']}")
            continue
        rows.append(offer_to_row(o, result, s, today))
        print(f"{n:>{width}} ✓ {s.score:3} | {o.company[:22]:22} | {o.title[:45]:45} | {sal:18} | {'; '.join(result.flags)}")
        print(f"{'':>{width}}         [{s.direction}] {s.summary}")
        if s.gaps:
            print(f"{'':>{width}}         braki: {', '.join(s.gaps)}")
    print(f"\n{total} ofert, {len(offers)} po deduplikacji, {rejected} odrzuconych przez triage, {len(errors)} błędów walidacji")
    for e in errors:
        print("  ", e)
    return rows


def run_gmail(days: int, process, ws, today: date) -> None:
    service = gmail_service()
    mail_log = None if ws is None else open_mail_log()
    ids = [m["id"] for m in list_messages(service, query=gmail_query(days), max_results=100)]
    if mail_log is not None:
        ids = unprocessed(ids, mail_log.col_values(1)[1:])
    print(f"[gmail] nowych maili: {len(ids)}")

    handle = make_handler(lambda message_id: get_message(service, message_id), load_mail_rules(), process)
    results = process_mails([{"id": i} for i in ids], handle)
    for r in results:
        status = f"BŁĄD {r.error}" if r.error else f"{len(r.rows)} ofert"
        print(f"[gmail] {r.mail_type:20} | {r.subject.strip()[:60]:60} | {status}")

    if ws is not None:
        rows = [row for r in results for row in r.rows]
        added, skipped = append_new(ws, rows)
        print(f"Arkusz: dopisano {added}, pominięto {skipped} (już były w arkuszu)")
        log_rows = processed_mail_rows(results, today)
        if log_rows:
            mail_log.append_rows(log_rows, value_input_option="RAW")

    if any(r.error for r in results):
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description="Ekstrakcja, triage i ocena ofert z pliku albo z Gmaila.")
    parser.add_argument("file", type=Path, nargs="?", help="plik z listą ofert albo treścią maila")
    parser.add_argument("--gmail", action="store_true", help="przetwórz nowe maile z etykiety oferty")
    parser.add_argument("--days", type=int, default=2, help="z ilu ostatnich dni brać maile (z --gmail)")
    parser.add_argument("--no-sheet", action="store_true", help="tylko wypisz wynik, bez zapisu do arkusza")
    args = parser.parse_args()
    if args.gmail == (args.file is not None):
        parser.error("podaj plik albo --gmail (dokładnie jedno z nich)")

    ws = None if args.no_sheet else open_worksheet()
    rules = load_rules()
    scoring_prompt = build_prompt(load_skills())
    today = date.today()

    def process(text: str) -> list[list]:
        return process_text(text, rules, scoring_prompt, today)

    if args.gmail:
        run_gmail(args.days, process, ws, today)
        return

    rows = process(args.file.read_text(encoding="utf-8"))

    if ws is None:
        print("Arkusz: pominięty (--no-sheet)")
        return
    added, skipped = append_new(ws, rows)
    print(f"Arkusz: dopisano {added}, pominięto {skipped} (już były w arkuszu)")


if __name__ == "__main__":
    main()