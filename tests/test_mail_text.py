import base64

from job_agent.mail_text import html_to_text, message_text


def enc(text: str) -> str:
    return base64.urlsafe_b64encode(text.encode("utf-8")).decode()


def test_html_to_text_keeps_lines_and_drops_tags():
    html = "<div>Data Engineer</div><div>Sii Polska</div><p>Poznań</p>"
    assert html_to_text(html) == "Data Engineer\nSii Polska\nPoznań"


def test_html_to_text_drops_style_and_empty_blocks():
    html = "<style>.a{color:red}</style><p>A</p><p></p><p></p><p>B</p>"
    assert html_to_text(html) == "A\nB"


def test_prefers_plain_text_in_nested_parts():
    payload = {"mimeType": "multipart/alternative", "parts": [
        {"mimeType": "text/html", "body": {"data": enc("<p>HTML</p>")}},
        {"mimeType": "text/plain", "body": {"data": enc("zwykły tekst")}},
    ]}
    assert message_text(payload) == "zwykły tekst"


def test_falls_back_to_html():
    payload = {"mimeType": "text/html", "body": {"data": enc("<p>Tylko HTML</p>")}}
    assert message_text(payload) == "Tylko HTML"


def test_empty_message():
    assert message_text({"mimeType": "multipart/mixed", "parts": []}) == ""