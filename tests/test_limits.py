from job_agent.limits import describe_limit

REAL_MESSAGE = (
    "Error code: 429 - {'error': {'message': 'Rate limit reached for model `openai/gpt-oss-120b` "
    "in organization `org_test` service tier `on_demand` on tokens per minute (TPM): "
    "Limit 8000, Used 4454, Requested 4222. Please try again in 5.07s.'}}"
)


def test_describes_tokens_per_minute():
    assert describe_limit(REAL_MESSAGE) == "limit: tokeny na minutę (4454/8000)"


def test_unknown_format_falls_back():
    assert describe_limit("zupełnie inny komunikat") == "limit zapytań Groq"