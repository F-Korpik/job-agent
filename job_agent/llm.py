import json
import os

from dotenv import load_dotenv
from groq import BadRequestError, Groq

load_dotenv()
_client = Groq(api_key=os.environ["GROQ_API_KEY"])
MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
MAX_ATTEMPTS = 3


def complete_json(system: str, user: str) -> dict:
    last_error: Exception | None = None
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            resp = _client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                response_format={"type": "json_object"},
                temperature=0,
            )
            return json.loads(resp.choices[0].message.content)
        except BadRequestError as e:
            if "json_validate_failed" not in str(e):
                raise
            last_error = e
            print(f"[llm] model zwrócił niepoprawny JSON, próba {attempt}/{MAX_ATTEMPTS}")
    raise last_error