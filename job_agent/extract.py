from pathlib import Path

from pydantic import ValidationError

from .chunk import chunk_lines
from .grounding import company_is_grounded
from .llm import complete_json
from .models import Offer


PROMPT = (Path(__file__).parent.parent / "prompts" / "extract_offers.md").read_text(encoding="utf-8")


def extract_offers(text: str, portal: str = "justjoin.it") -> tuple[list[Offer], list[str]]:
    chunks = chunk_lines(text)
    print(f"[extract] tekst podzielony na {len(chunks)} kawałków")
    offers, errors = [], []
    for n, chunk in enumerate(chunks, start=1):
        print(f"[extract] kawałek {n}/{len(chunks)}")
        data = complete_json(PROMPT, chunk)
        for i, raw in enumerate(data.get("offers", [])):
            try:
                offers.append(Offer(**{**raw, "portal": portal}))
            except ValidationError as e:
                err = e.errors()[0]
                field = ".".join(str(part) for part in err["loc"])
                errors.append(
                    f"kawałek {n}, oferta {i} ({raw.get('title', '?')}): "
                    f"pole {field} = {err['input']!r} → {err['msg']}"
                )
    for offer in offers:
        offer.grounded = company_is_grounded(offer.company, offer.title, text)
    return offers, errors