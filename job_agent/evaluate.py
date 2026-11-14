import csv
from dataclasses import dataclass, field
from pathlib import Path

from .dedup import normalize
from .models import Offer


@dataclass
class EvalResult:
    expected_count: int
    got_count: int
    correct: list[tuple[str, str]] = field(default_factory=list)
    wrong_company: list[tuple[str, str, str]] = field(default_factory=list)
    missing: list[tuple[str, str]] = field(default_factory=list)
    extra: list[tuple[str, str]] = field(default_factory=list)

    @property
    def recall(self) -> float:
        return len(self.correct) / self.expected_count if self.expected_count else 0.0

    @property
    def precision(self) -> float:
        return len(self.correct) / self.got_count if self.got_count else 0.0


def load_expected(path: Path) -> list[tuple[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        return [(row["firma"], row["tytul"]) for row in csv.DictReader(f)]


def compare(expected: list[tuple[str, str]], got: list[Offer]) -> EvalResult:
    companies_by_title: dict[str, set[str]] = {}
    for company, title in expected:
        companies_by_title.setdefault(normalize(title), set()).add(normalize(company))

    result = EvalResult(expected_count=len(expected), got_count=len(got))
    matched: set[tuple[str, str]] = set()
    wrong_titles: set[str] = set()

    for offer in got:
        title, company = normalize(offer.title), normalize(offer.company)
        expected_companies = companies_by_title.get(title)
        if expected_companies is None:
            result.extra.append((offer.company, offer.title))
        elif company in expected_companies:
            result.correct.append((offer.company, offer.title))
            matched.add((company, title))
        else:
            result.wrong_company.append((offer.title, offer.company, ", ".join(sorted(expected_companies))))
            wrong_titles.add(title)

    for company, title in expected:
        key = (normalize(company), normalize(title))
        if key not in matched and key[1] not in wrong_titles:
            result.missing.append((company, title))
    return result