"""One test per requirement in docs/requirements.md."""
from admissions import AdmissionEngine, Applicant, RecommendationAnalyzer, validate_registration


def make(email="test.user@gmail.com", **kw):
    data = dict(first_name="Test", last_name="User", sat=1200, ec=3, gpa=3.0, interview=3, rec_text="")
    data.update(kw)
    return Applicant(email=email, **data)


def test_req01_every_applicant_gets_a_unique_id():
    ids = {make().user_id for _ in range(200)}
    assert len(ids) == 200


def test_req02_duplicate_email_is_detected():
    engine = AdmissionEngine()
    engine.applicants["test.user@gmail.com"] = make()
    assert engine.is_email_taken("test.user@gmail.com")
    assert not engine.is_email_taken("someone.else@gmail.com")


def test_req05_only_gmail_addresses_pass():
    assert validate_registration("Ada", "Lovelace", "ada.lovelace@gmail.com") is None
    assert validate_registration("Ada", "Lovelace", "ada@yahoo.com")
    assert validate_registration("Ada", "Lovelace", "ab@gmail.com")  # too short


def test_names_reject_digits_symbols_and_blanks():
    assert validate_registration("John123", "Doe", "john.doe@gmail.com")
    assert validate_registration("Alice", "Smith!", "alice.smith@gmail.com")
    assert validate_registration("", "Doe", "john.doe@gmail.com")
    assert validate_registration("Çağrı", "Öztürk", "cagri.ozturk@gmail.com") is None


def test_req04_higher_scores_rank_first():
    engine = AdmissionEngine()
    engine.applicants["strong.one@gmail.com"] = make("strong.one@gmail.com", sat=1600, ec=5, gpa=4.0, interview=5)
    engine.applicants["weaker.one@gmail.com"] = make("weaker.one@gmail.com", sat=900, ec=1, gpa=2.0, interview=1)
    engine.calculate_rankings()
    assert engine.ranked()[0].email == "strong.one@gmail.com"


def test_weights_change_the_order():
    engine = AdmissionEngine()
    engine.applicants["sat.star@gmail.com"] = make("sat.star@gmail.com", sat=1600, ec=1)
    engine.applicants["club.star@gmail.com"] = make("club.star@gmail.com", sat=900, ec=5)
    engine.calculate_rankings({"SAT": 1.0, "EC": 0, "GPA": 0, "INT": 0, "REC": 0})
    assert engine.ranked()[0].email == "sat.star@gmail.com"
    engine.calculate_rankings({"SAT": 0, "EC": 1.0, "GPA": 0, "INT": 0, "REC": 0})
    assert engine.ranked()[0].email == "club.star@gmail.com"


def test_req06_changes_are_logged():
    app = make()
    before = len(app.audit_log)
    app.add_log("Updated SAT to 1400")
    assert len(app.audit_log) == before + 1


def test_req07_scholarship_tiers():
    engine = AdmissionEngine()
    engine.applicants["top.student@gmail.com"] = make("top.student@gmail.com", sat=1580, ec=5, gpa=3.95)
    engine.applicants["merit.student@gmail.com"] = make("merit.student@gmail.com", sat=1460)
    engine.applicants["regular.student@gmail.com"] = make("regular.student@gmail.com", sat=1100, gpa=3.0)
    engine.calculate_rankings()
    tiers = {email: app.scholarship_status for email, app in engine.applicants.items()}
    assert tiers["top.student@gmail.com"].startswith("Presidential")
    assert tiers["merit.student@gmail.com"].startswith("Merit")
    assert tiers["regular.student@gmail.com"] == "Standard"


def test_letter_analysis_scores_and_traits():
    analyzer = RecommendationAnalyzer()
    score, strengths, _ = analyzer.analyze_letter("An outstanding, excellent student who led our python team.")
    assert score >= 4
    assert {"Leadership", "Technical Skills", "Teamwork"} <= set(strengths)

    low, _, _ = analyzer.analyze_letter("He was often late and struggled with weak work.")
    assert low <= 2

    assert analyzer.analyze_letter("")[0] == 3
