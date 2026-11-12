import json
import os
import re

from datetime import datetime, timedelta
from dotenv import load_dotenv
from groq import BadRequestError, Groq


load_dotenv()
_client = Groq(api_key=os.environ["GROQ_API_KEY"])
MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
MAX_ATTEMPTS = 3


LIMIT_NAMES = {
    "TPM": "tokeny na minutę",
    "TPD": "tokeny na dzień",
    "RPM": "zapytania na minutę",
    "RPD": "zapytania na dzień",
}


def _limit_info(e: RateLimitError) -> str:
    m = re.search(r"\((TPM|TPD|RPM|RPD)\): Limit (\d+), Used (\d+)", str(e))
    if not m:
        return "limit zapytań Groq"
    kind, limit, used = m.groups()
    return f"limit: {LIMIT_NAMES[kind]} ({used}/{limit})"


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
            waits += 1
            wait = _wait_seconds(e)
            info = _limit_info(e)
            if wait > MAX_WAIT_S:
                print(f"[llm] {info}. Groq każe czekać ok. {wait / 60:.0f} min, to prawdopodobnie limit dzienny. Przerywam.")
                raise
            if waits > MAX_RATE_LIMIT_WAITS:
                print(f"[llm] {info}. Limit trafiony {MAX_RATE_LIMIT_WAITS} razy przy jednym kawałku. Przerywam.")
                raise
            resume_at = (datetime.now() + timedelta(seconds=wait)).strftime("%H:%M:%S")
            print(f"[llm] {info}. Czekam {wait:.0f} s, wznowienie ok. {resume_at} ({waits}/{MAX_RATE_LIMIT_WAITS})")
            time.sleep(wait)
    raise last_error