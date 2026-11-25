from job_agent.gmail import gmail_service, list_messages, message_headers

service = gmail_service()
for m in list_messages(service):
    h = message_headers(service, m["id"])
    print(f"{h.get('Date', '')[:16]:16} | {h.get('From', '')[:40]:40} | {h.get('Subject', '')[:70]}")