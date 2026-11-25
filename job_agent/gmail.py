import os
from pathlib import Path

from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
CLIENT_FILE = Path(os.getenv("GMAIL_CLIENT_FILE", "oauth-client.json"))
TOKEN_FILE = Path(os.getenv("GMAIL_TOKEN_FILE", "gmail-token.json"))
LABEL = "oferty"


def get_credentials() -> Credentials:
    creds = None
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
    if creds and creds.valid:
        return creds
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_FILE), SCOPES)
        creds = flow.run_local_server(port=0)
    TOKEN_FILE.write_text(creds.to_json(), encoding="utf-8")
    return creds


def gmail_service():
    return build("gmail", "v1", credentials=get_credentials())


def list_messages(service, query: str = f"label:{LABEL}", max_results: int = 20) -> list[dict]:
    response = service.users().messages().list(userId="me", q=query, maxResults=max_results).execute()
    return response.get("messages", [])


def message_headers(service, message_id: str) -> dict:
    message = service.users().messages().get(
        userId="me", id=message_id, format="metadata", metadataHeaders=["From", "Subject", "Date"]
    ).execute()
    return {h["name"]: h["value"] for h in message["payload"]["headers"]}