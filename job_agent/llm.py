import json
import os
import time
from datetime import datetime, timedelta

from dotenv import load_dotenv
from groq import BadRequestError, Groq, RateLimitError

from .limits import describe_limit

load_dotenv()
_client = Groq(api_key=os.environ["GROQ_API_KEY"])
MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
MAX_ATTEMPTS = 3
MAX_RATE_LIMIT_WAITS = 5
MAX_WAIT_S = 120
DEFAULT_WAIT_S = 20


def _wait_seconds(e: RateLimitError) -> float:
    value = e.response.headers.get("retry-after")
    try:
        return float(value) + 1
    except (TypeError, ValueError):
        return DEFAULT_WAIT_S


def complete_json(system: str, user: str) -> dict:
    last_error: Exception | None = None
    attempts = 0
    waits = 0
    while attempts < MAX_ATTEMPTS:
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
        except RateLimitError as e:
            waits += 1
            wait = _wait_seconds(e)
            info = describe_limit(str(e))
            if wait > MAX_WAIT_S:
                print(f"[llm] {info}. Groq każe czekać ok. {wait / 60:.0f} min, to prawdopodobnie limit dzienny. Przerywam.")
                raise
            if waits > MAX_RATE_LIMIT_WAITS:
                print(f"[llm] {info}. Limit trafiony {MAX_RATE_LIMIT_WAITS} razy przy jednym kawałku. Przerywam.")
                raise
            resume_at = (datetime.now() + timedelta(seconds=wait)).strftime("%H:%M:%S")
            print(f"[llm] {info}. Czekam {wait:.0f} s, wznowienie ok. {resume_at} ({waits}/{MAX_RATE_LIMIT_WAITS})")
            time.sleep(wait)
        except BadRequestError as e:
            if "json_validate_failed" not in str(e):
                raise
            attempts += 1
            last_error = e
            print(f"[llm] model zwrócił niepoprawny JSON, próba {attempts}/{MAX_ATTEMPTS}")
    raise last_error