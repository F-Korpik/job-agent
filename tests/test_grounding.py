from job_agent.grounding import company_is_grounded

RAW = """Super offer
Sii
Sii

Show profile
Remote

Technical Lead — Data Science (f/m/x)
14d left
Python
Mid
Permanent
Full-time
Momentum
Momentum

Wrocław

Remote

Machine Learning Engineer
17d left
Python
Full-time
C&F
C&F

Show profile
Warszawa

Remote

Azure Support Engineer
Full-time
G2A
G2A"""

COMPACT = """FarmaProm | Poznań | Hybrid
Analytics Engineer | https://justjoin.it/job-offer/farmaprom-analytics-engineer-poznan-data
4d left | Undisclosed Salary | SQL, Python"""


def test_correct_company_is_grounded():
    assert company_is_grounded("Momentum", "Machine Learning Engineer", RAW)
    assert company_is_grounded("Sii", "Technical Lead — Data Science (f/m/x)", RAW)


def test_company_from_previous_offer_is_not_grounded():
    assert not company_is_grounded("Sii", "Machine Learning Engineer", RAW)


def test_company_from_next_offer_is_not_grounded():
    assert not company_is_grounded("Momentum", "Technical Lead — Data Science (f/m/x)", RAW)
    assert not company_is_grounded("G2A", "Azure Support Engineer", RAW)


def test_compact_format():
    assert company_is_grounded("FarmaProm", "Analytics Engineer", COMPACT)


def test_title_not_in_source():
    assert not company_is_grounded("FarmaProm", "Senior Data Engineer", COMPACT)


def test_company_must_be_whole_word():
    assert not company_is_grounded("Sii", "Mission Engineer", "Mission Engineer")