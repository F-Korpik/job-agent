import re

from .dedup import normalize

WINDOW = 10


def _contains_word(text: str, phrase: str) -> bool:
    return re.search(rf"(?<!\w){re.escape(phrase)}(?!\w)", text) is not None


def company_is_grounded(company: str, title: str, source: str, window: int = WINDOW) -> bool:
    lines = [normalize(line) for line in source.splitlines()]
    company_n, title_n = normalize(company), normalize(title)
    if not company_n or not title_n:
        return False
    for i, line in enumerate(lines):
        if title_n in line:
            above = lines[max(0, i - window): i + 1]
            if any(_contains_word(candidate, company_n) for candidate in above):
                return True
    return False