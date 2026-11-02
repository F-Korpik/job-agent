import json
import os

from dotenv import load_dotenv
from groq import Groq

load_dotenv()
_client = Groq(api_key=os.environ["GROQ_API_KEY"])
MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")


def complete_json(system: str, user: str) -> dict:
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