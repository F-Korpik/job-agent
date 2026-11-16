import sys
from pathlib import Path

from .dedup import deduplicate
from .extract import extract_offers
from .triage import load_rules, triage


def main() -> None:
    text = Path(sys.argv[1]).read_text(encoding="utf-8")
    offers, errors = extract_offers(text)
    total = len(offers)
    offers = deduplicate(offers)
    width = len(str(len(offers)))
    rules = load_rules()
    rejected = 0
    for n, o in enumerate(offers, start=1):
        result = triage(o, rules)
        if result.decision == "reject":
            rejected += 1
        mark = "✗" if result.decision == "reject" else "✓"
        sal = f"{o.salary_min}-{o.salary_max} {o.currency}" if o.salary_min else "brak widełek"
        note = "; ".join(result.reasons or result.flags)
        print(f"{n:>{width}} {mark} | {o.company[:22]:22} | {o.title[:45]:45} | {sal:18} | {note}")
    print(f"\n{total} ofert, {len(offers)} po deduplikacji, {rejected} odrzuconych przez triage, {len(errors)} błędów walidacji")
    for e in errors:
        print("  ", e)


if __name__ == "__main__":
    main()