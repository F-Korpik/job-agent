from .dedup import normalize


def chunk_lines(text: str, max_lines: int = 40, overlap: int = 10) -> list[str]:
    if overlap >= max_lines:
        raise ValueError("overlap musi być mniejszy niż max_lines")
    lines = text.splitlines()
    if len(lines) <= max_lines:
        return [text]
    chunks = []
    step = max_lines - overlap
    for start in range(0, len(lines), step):
        chunks.append("\n".join(lines[start:start + max_lines]))
        if start + max_lines >= len(lines):
            break
    return chunks


END_MARKERS = {"full-time", "part-time", "freelance", "aplikuj"}


def offer_boundaries(lines: list[str]) -> list[int]:
    normalized = [normalize(line) for line in lines]
    markers = [i for i, line in enumerate(normalized) if line in END_MARKERS]
    if markers:
        return markers
    return [i for i, line in enumerate(normalized) if line == ""]


def chunk_by_offers(text: str, max_lines: int = 40) -> list[str]:
    lines = text.splitlines()
    if len(lines) <= max_lines:
        return [text]

    segments: list[list[str]] = []
    start = 0
    for end in offer_boundaries(lines):
        segments.append(lines[start:end + 1])
        start = end + 1
    if start < len(lines):
        segments.append(lines[start:])

    chunks: list[list[str]] = []
    current: list[str] = []
    for segment in segments:
        if len(segment) > max_lines:
            if current:
                chunks.append(current)
                current = []
            for piece in chunk_lines("\n".join(segment), max_lines=max_lines):
                chunks.append(piece.splitlines())
            continue
        if current and len(current) + len(segment) > max_lines:
            chunks.append(current)
            current = []
        current.extend(segment)
    if current:
        chunks.append(current)

    return ["\n".join(chunk) for chunk in chunks]    