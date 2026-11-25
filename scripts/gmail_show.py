import sys

from job_agent.gmail import get_message, gmail_service, list_messages
from job_agent.mail_text import message_text

query = sys.argv[1] if len(sys.argv) > 1 else "label:oferty"
service = gmail_service()
first = list_messages(service, query=query, max_results=1)[0]
print(message_text(get_message(service, first["id"])["payload"]))