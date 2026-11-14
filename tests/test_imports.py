import importlib

import pytest

MODULES = [
    "job_agent.chunk",
    "job_agent.dedup",
    "job_agent.evaluate",
    "job_agent.extract",
    "job_agent.grounding",
    "job_agent.limits",
    "job_agent.llm",
    "job_agent.models",
    "job_agent.__main__",
    "scripts.eval_extraction",
]


@pytest.mark.parametrize("name", MODULES)
def test_module_imports(name, monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test-key-not-real")
    importlib.import_module(name)