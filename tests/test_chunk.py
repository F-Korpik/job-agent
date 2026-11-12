import pytest

from job_agent.chunk import chunk_lines


def make_text(n: int) -> str:
    return "\n".join(f"linia {i}" for i in range(n))


def test_short_text_is_one_chunk():
    assert chunk_lines(make_text(10), max_lines=40) == [make_text(10)]


def test_every_line_is_in_some_chunk():
    text = make_text(100)
    chunks = chunk_lines(text, max_lines=40, overlap=10)
    covered = {line for c in chunks for line in c.splitlines()}
    assert covered == set(text.splitlines())


def test_neighbouring_chunks_overlap():
    chunks = chunk_lines(make_text(100), max_lines=40, overlap=10)
    for a, b in zip(chunks, chunks[1:]):
        assert a.splitlines()[-10:] == b.splitlines()[:10]


def test_overlap_must_be_smaller_than_chunk():
    with pytest.raises(ValueError):
        chunk_lines(make_text(100), max_lines=10, overlap=10)