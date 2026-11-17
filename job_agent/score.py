from pathlib import Path

import yaml

from .llm import complete_json
from .models import Offer, Score

ROOT = Path(__file__).parent.parent
PROMPT_PATH = ROOT / "prompts" / "score_offer.md"
SKILLS_PATH = ROOT / "profile" / "skills.yaml"


def load_skills(path: Path = SKILLS_PATH) -> dict:
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def skills_for_scoring(skills: dict) -> str:
    lines = []
    for section in skills["scoring_sections"]:
        for name, level in skills["sections"][section].items():
            lines.append(f"- {name}: {level}")
    return "\n".join(lines)


def build_prompt(skills: dict) -> str:
    template = PROMPT_PATH.read_text(encoding="utf-8")
    return template.replace("{{SKILLS}}", skills_for_scoring(skills))


def describe_offer(offer: Offer) -> str:
    if offer.salary_min:
        salary = f"{offer.salary_min}–{offer.salary_max} {offer.currency or ''} ({offer.salary_period or 'okres nieznany'})"
    else:
        salary = "brak widełek"
    return "\n".join([
        f"Tytuł: {offer.title}",
        f"Firma: {offer.company}",
        f"Lokalizacja: {offer.location or 'brak'}",
        f"Tryb pracy: {offer.work_mode or 'brak'}",
        f"Umowa: {', '.join(offer.contract_types) or 'brak'}",
        f"Widełki: {salary}",
        f"Tagi: {', '.join(offer.tags) or 'brak'}",
    ])


def score_offer(offer: Offer, system_prompt: str) -> Score:
    return Score(**complete_json(system_prompt, describe_offer(offer)))