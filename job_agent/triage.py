from pathlib import Path

import yaml

CONFIG_PATH = Path(__file__).parent.parent / "config" / "triage.yaml"


def load_rules(path: Path = CONFIG_PATH) -> dict:
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)