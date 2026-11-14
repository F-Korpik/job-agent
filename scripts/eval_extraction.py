import argparse
from pathlib import Path

from job_agent.dedup import deduplicate
from job_agent.evaluate import compare, load_expected
from job_agent.extract import extract_offers

EXPECTED_DIR = Path("tests/eval/expected")


def main() -> None:
    parser = argparse.ArgumentParser(description="Ewaluacja ekstrakcji ofert względem wzorca")
    parser.add_argument("fixture", type=Path, help="plik z listą ofert, np. tests/fixtures/jjit_poznan_2026-11-03.txt")
    parser.add_argument("--runs", type=int, default=1, help="ile razy powtórzyć ekstrakcję (domyślnie 1)")
    args = parser.parse_args()

    expected_path = EXPECTED_DIR / f"{args.fixture.stem}.csv"
    expected = load_expected(expected_path)
    text = args.fixture.read_text(encoding="utf-8")

    summary = []
    for run in range(1, args.runs + 1):
        offers, errors = extract_offers(text)
        r = compare(expected, deduplicate(offers))
        summary.append(f"{len(r.correct)}/{r.expected_count}")

        print(f"\n=== przebieg {run}/{args.runs} ===")
        print(
            f"poprawne {len(r.correct)}/{r.expected_count} | zła firma {len(r.wrong_company)} | "
            f"zgubione {len(r.missing)} | śmieciowe {len(r.extra)} | błędy walidacji {len(errors)}"
        )
        print(f"recall {r.recall:.0%} | precision {r.precision:.0%}")
        for title, got, exp in r.wrong_company:
            print(f"  zła firma:  {title!r}: jest {got!r}, powinno być {exp!r}")
        for company, title in r.missing:
            print(f"  zgubiona:   {company} – {title}")
        for company, title in r.extra:
            print(f"  śmieciowa:  {company} – {title}")

    print(f"\nPodsumowanie {args.fixture.name}: {', '.join(summary)}")


if __name__ == "__main__":
    main()