import base64
from html.parser import HTMLParser

BLOCK_TAGS = {"p", "div", "br", "tr", "td", "li", "h1", "h2", "h3", "h4", "table"}
SKIP_TAGS = {"style", "script"}


class _TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
        self.skip = 0

    def _newline(self):
        if self.parts and not "".join(self.parts).rstrip(" \t").endswith("\n"):
            self.parts.append("\n")

    def handle_starttag(self, tag, attrs):
        if tag in SKIP_TAGS:
            self.skip += 1
        if tag == "br":
            self.parts.append("\n")
        elif tag in BLOCK_TAGS:
            self._newline()

    def handle_endtag(self, tag):
        if tag in SKIP_TAGS:
            self.skip -= 1
        if tag in BLOCK_TAGS and tag != "br":
            self._newline()

    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data.replace("\n", " "))


def html_to_text(html: str) -> str:
    parser = _TextExtractor()
    parser.feed(html)
    lines = [" ".join(line.split()) for line in "".join(parser.parts).splitlines()]
    out = []
    for line in lines:
        if line or (out and out[-1]):
            out.append(line)
    return "\n".join(out).strip()


def _decode(data: str) -> str:
    padded = data + "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(padded).decode("utf-8", errors="replace")


def _find_part(payload: dict, mime_type: str) -> str | None:
    if payload.get("mimeType") == mime_type and payload.get("body", {}).get("data"):
        return payload["body"]["data"]
    for part in payload.get("parts", []):
        if found := _find_part(part, mime_type):
            return found
    return None


def message_text(payload: dict) -> str:
    if data := _find_part(payload, "text/plain"):
        return _decode(data)
    if data := _find_part(payload, "text/html"):
        return html_to_text(_decode(data))
    return ""