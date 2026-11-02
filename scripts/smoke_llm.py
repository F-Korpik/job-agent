from job_agent.llm import MODEL, complete_json

result = complete_json(
    system='Odpowiadaj wyłącznie w JSON.',
    user='Zwróć obiekt {"ok": true}.',
)
print(f"model: {MODEL}")
print(result)