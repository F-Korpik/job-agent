from pathlib import Path

from pydantic import ValidationError

from .llm import complete_json
from .models import Offer

PROMPT = (Path(__file__).parent.parent / "prompts" / "extract_offers.md").read_text(encoding="utf-8")


def extract_offers(text: str, portal: str = "justjoin.it") -> tuple[list[Offer], list[str]]:
    data = complete_json(PROMPT, text)
    offers, errors = [], []
    for i, raw in enumerate(data.get("offers", [])):
        try:
            offers.append(Offer(**{**raw, "portal": portal}))
        except ValidationError as e:
            errors.append(f"oferta {i} ({raw.get('title', '?')}): {e.errors()[0]['msg']}")
    return offers, errors