from dataclasses import dataclass
from email.utils import parseaddr
from pathlib import Path

import yaml

from .dedup import normalize

CONFIG_PATH = Path(__file__).parent.parent / "config" / "mail_types.yaml"


@dataclass
class MailType:
    name: str
    process: bool


UNKNOWN = MailType("nieznany", False)


def load_mail_rules(path: Path = CONFIG_PATH) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)["types"]


def classify(sender: str, subject: str, rules: list[dict]) -> MailType:
    address = parseaddr(sender)[1].lower()
    subject = normalize(subject)
    for rule in rules:
        if address != rule["sender"]:
            continue
        if "subject" in rule and normalize(rule["subject"]) not in subject:
            continue
        return MailType(rule["name"], rule["process"])
    return UNKNOWN