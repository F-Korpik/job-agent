import argparse
from datetime import date
from pathlib import Path

from pydantic import ValidationError

from .dedup import deduplicate
from .extract import extract_offers
from .score import build_prompt, load_skills, score_offer
from .sheets import append_new, offer_to_row, open_worksheet
from .triage import load_rules, triage


def main() -> None:
    parser = argparse.ArgumentParser(description="Ekstrakcja, triage i ocena ofert z pliku tekstowego.")
    parser.add_argument("file", type=Path, help="plik z listą ofert albo treścią maila")
    parser.add_argument("--no-sheet", action="store_true", help="tylko wypisz wynik, bez zapisu do arkusza")
    args = parser.parse_args()

    ws = None if args.no_sheet else open_worksheet()
    text = args.file.read_text(encoding="utf-8")
    offers, errors = extract_offers(text)
    total = len(offers)
    offers = deduplicate(offers)
    rules = load_rules()
    scoring_prompt = build_prompt(load_skills())
    width = len(str(len(offers)))
    today = date.today()
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

    if ws is None:
        print("Arkusz: pominięty (--no-sheet)")
        return
    added, skipped = append_new(ws, rows)
    print(f"Arkusz: dopisano {added}, pominięto {skipped} (już były w arkuszu)")


if __name__ == "__main__":
    main()