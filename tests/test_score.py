from pathlib import Path

import pytest
from pydantic import ValidationError

from job_agent import score
from job_agent.score import build_prompt, clamp_to_band, describe_offer, score_offer, skills_for_scoring
from job_agent.models import Offer, Score


SKILLS = score.load_skills(Path(__file__).parent / "fixtures" / "skills_example.yaml")


def test_prompt_contains_only_scoring_sections():
    prompt = score.build_prompt(SKILLS)
    assert "Python: średniozaawansowany" in prompt
    assert "API LLM" in prompt
    assert "SolidWorks" not in prompt
    assert "{{SKILLS}}" not in prompt


def test_describe_offer_with_salary_period():
    o = Offer(company="X", title="AI Engineer", salary_min=188000, salary_max=282000, currency="PLN", salary_period="year")
    assert "188000–282000 PLN (year)" in score.describe_offer(o)


def test_describe_offer_without_salary():
    assert "Widełki: brak widełek" in score.describe_offer(Offer(company="X", title="Y"))


def test_score_out_of_range_rejected():
    with pytest.raises(ValidationError):
        Score(score=150, summary="x")


def test_score_offer_with_fake_model(monkeypatch):
    fake = {"score": 85, "direction": "docelowy", "summary": "Pasuje.", "gaps": ["Airflow"], "red_flags": []}
    monkeypatch.setattr(score, "complete_json", lambda system, user: fake)
    result = score.score_offer(Offer(company="X", title="Y"), "prompt")
    assert result.score == 85 and result.gaps == ["Airflow"]


@pytest.mark.parametrize("direction, raw, expected", [
    ("pokrewny", 70, 55),   # za wysoko → przycięte do góry przedziału
    ("pokrewny", 40, 40),   # w przedziale → bez zmian
    ("docelowy", 45, 60),   # za nisko → podniesione do dołu przedziału
    ("inny", 50, 25),
])
def test_clamp_to_band(direction, raw, expected):
    score = Score(score=raw, direction=direction, summary="x")
    assert clamp_to_band(score).score == expected


def test_direction_case_insensitive():
    assert Score(score=50, direction="Pokrewny", summary="x").direction == "pokrewny"


def test_unknown_direction_rejected():
    with pytest.raises(ValidationError):
        Score(score=50, direction="średni", summary="x")