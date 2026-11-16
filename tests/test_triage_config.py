from job_agent.triage import load_rules



def test_config_loads():
    rules = load_rules()
    assert rules["min_salary_uop_monthly"] == 8300
    assert "reject" in rules and "flag" in rules


def test_every_rule_is_complete():
    rules = load_rules()
    for section in ("reject", "flag"):
        for name, rule in rules[section].items():
            assert rule["reason"], name
            assert rule["words"], name
            assert set(rule["fields"]) <= {"title", "tags"}, name