import sys
from pathlib import Path

from .extract import extract_offers


def main() -> None:
    text = Path(sys.argv[1]).read_text(encoding="utf-8")
    offers, errors = extract_offers(text)
    for o in offers:
        sal = f"{o.salary_min}-{o.salary_max} {o.currency}" if o.salary_min else "brak widełek"
        print(f"{o.company[:22]:22} | {o.title[:45]:45} | {o.work_mode or '?':6} | {sal}")
    print(f"\n{len(offers)} ofert, {len(errors)} błędów walidacji")
    for e in errors:
        print("  ", e)


if __name__ == "__main__":
    main()