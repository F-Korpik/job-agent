import sys
from pathlib import Path

from pydantic import ValidationError

from .dedup import deduplicate
from .extract import extract_offers
from .score import build_prompt, load_skills, score_offer
from .triage import load_rules, triage


def main() -> None:
    text = Path(sys.argv[1]).read_text(encoding="utf-8")
    offers, errors = extract_offers(text)
    total = len(offers)
    offers = deduplicate(offers)
    width = len(str(len(offers)))
    rules = load_rules()
    scoring_prompt = build_prompt(load_skills())
    rejected = 0
    for n, o in enumerate(offers, start=1):
        result = triage(o, rules)
        sal = f"{o.salary_min}-{o.salary_max} {o.currency}" if o.salary_min else "brak widełek"
        if result.decision == "reject":
            rejected += 1
            print(f"{n:>{width}} ✗   - | {o.company[:22]:22} | {o.title[:45]:45} | {sal:18} | {'; '.join(result.reasons)}")
            continue
        try:
            s = score_offer(o, scoring_prompt)
        except ValidationError as e:
            print(f"{n:>{width}} ✓   ? | {o.company[:22]:22} | {o.title[:45]:45} | błąd oceny: {e.errors()[0]['msg']}")
            continue
        print(f"{n:>{width}} ✓ {s.score:3} | {o.company[:22]:22} | {o.title[:45]:45} | {sal:18} | {'; '.join(result.flags)}")
        print(f"{'':>{width}}         [{s.direction}] {s.summary}")
        if s.gaps:
            print(f"{'':>{width}}         braki: {', '.join(s.gaps)}")
    print(f"\n{total} ofert, {len(offers)} po deduplikacji, {rejected} odrzuconych przez triage, {len(errors)} błędów walidacji")
    for e in errors:
        print("  ", e)


if __name__ == "__main__":
    main()