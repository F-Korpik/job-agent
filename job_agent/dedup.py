import hashlib
import re

from .models import Offer


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def offer_key(offer: Offer) -> str:
    text = f"{normalize(offer.company)}|{normalize(offer.title)}"
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:12]


def deduplicate(offers: list[Offer]) -> list[Offer]:
    seen: set[str] = set()
    unique: list[Offer] = []
    for offer in offers:
        key = offer_key(offer)
        if key not in seen:
            seen.add(key)
            unique.append(offer)
    return unique

