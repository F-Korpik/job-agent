import pytest
from pydantic import ValidationError

from job_agent.models import Offer


def test_work_mode_is_case_insensitive():
    assert Offer(company="X", title="Y", work_mode="Hybrid").work_mode == "hybrid"


def test_unknown_work_mode_still_rejected():
    with pytest.raises(ValidationError):
        Offer(company="X", title="Y", work_mode="sometimes")


def test_salary_period_is_case_insensitive():
    assert Offer(company="X", title="Y", salary_period="Month").salary_period == "month"


def test_unknown_work_mode_still_rejected():
    with pytest.raises(ValidationError):
        Offer(company="X", title="Y", work_mode="sometimes")