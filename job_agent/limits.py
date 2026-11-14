import re

LIMIT_NAMES = {
    "TPM": "tokeny na minutę",
    "TPD": "tokeny na dzień",
    "RPM": "zapytania na minutę",
    "RPD": "zapytania na dzień",
}


def describe_limit(message: str) -> str:
    m = re.search(r"\((TPM|TPD|RPM|RPD)\): Limit (\d+), Used (\d+)", message)
    if not m:
        return "limit zapytań Groq"
    kind, limit, used = m.groups()
    return f"limit: {LIMIT_NAMES[kind]} ({used}/{limit})"