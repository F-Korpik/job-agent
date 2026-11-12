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