from pathlib import Path
from dataclasses import dataclass, field

import yaml

from .dedup import normalize
from .grounding import contains_word
from .models import Offer

CONFIG_PATH = Path(__file__).parent.parent / "config" / "triage.yaml"


def load_rules(path: Path = CONFIG_PATH) -> dict:
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def matches_rule(offer: Offer, rule: dict) -> bool:
    for field in rule["fields"]:
        if field == "title":
            text = offer.title
        else:
            text = " | ".join(offer.tags)
        text = normalize(text)

        for word in rule["words"]:
            if contains_word(text, normalize(word)):
                return True
    return False


@dataclass
class TriageResult:
    decision: str
    reasons: list[str] = field(default_factory=list)
    flags: list[str] = field(default_factory=list)


def _salary_too_low(offer: Offer, min_monthly: int) -> bool:
    return (
        offer.contract_types == ["UoP"]
        and offer.salary_period == "month"
        and offer.salary_max is not None
        and offer.salary_max < min_monthly
    )


def triage(offer: Offer, rules: dict) -> TriageResult:
    reasons = []
    if offer.contract_types == ["B2B"]:
        reasons.append("tylko B2B")
    if _salary_too_low(offer, rules["min_salary_uop_monthly"]):
        reasons.append(f"widełki UoP poniżej {rules['min_salary_uop_monthly']} zł")
    for rule in rules["reject"].values():
        if matches_rule(offer, rule):
            reasons.append(rule["reason"])

    if reasons:
        return TriageResult("reject", reasons)
    flags = [rule["reason"] for rule in rules["flag"].values() if matches_rule(offer, rule)]
    return TriageResult("pass", flags=flags)
