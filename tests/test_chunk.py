import pytest

from job_agent.chunk import chunk_lines, offer_boundaries


RAW = [
    "Sii", "Sii", "", "Remote", "", "Technical Lead — Data Science", "Python", "Full-time",
    "Momentum", "Momentum", "", "Wrocław", "", "Remote", "", "Machine Learning Engineer", "Full-time",
]

COMPACT = [
    "FarmaProm | Poznań | Hybrid",
    "Analytics Engineer | https://justjoin.it/x",
    "4d left | Undisclosed Salary | SQL | Mid, Permanent, Full-time",
    "",
    "Miele Global Services | Poznań | Remote",
    "SAP Data Engineer | https://justjoin.it/y",
    "10d left | 13 400 - 17 300 PLN/month | SAP | Mid, Permanent, Full-time",
]

MAIL = ["Cześć", "DCV Technologies", "AI/ML Engineer", "Aplikuj", "Link Group", "AI Engineer with French", "Aplikuj"]


def test_raw_format_cuts_after_full_time_only():
    assert offer_boundaries(RAW) == [7, 16]


def test_compact_format_cuts_on_blank_lines():
    assert offer_boundaries(COMPACT) == [3]


def test_mail_format_cuts_after_aplikuj():
    assert offer_boundaries(MAIL) == [3, 6]


def test_markers_are_normalized():
    assert offer_boundaries(["Oferta", "  FULL-TIME  "]) == [1]


def test_no_boundaries():
    assert offer_boundaries(["jedna linijka", "druga linijka"]) == []


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