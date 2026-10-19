"""Logic layer: validation, weighted ranking and scholarship rules."""
import re

NAME_PATTERN = r"^[A-Za-zÇçĞğİıÖöŞşÜü]+$"
EMAIL_PATTERN = r"^[a-z0-9](\.?[a-z0-9]){5,}@gmail\.com$"  # REQ-05

DEFAULT_WEIGHTS = {"SAT": 0.2, "EC": 0.2, "GPA": 0.2, "INT": 0.2, "REC": 0.2}


def validate_registration(first_name, last_name, email):
    """Return an error message, or None when the input is valid."""
    if not first_name or not re.match(NAME_PATTERN, first_name):
        return "First name must contain letters only."
    if not last_name or not re.match(NAME_PATTERN, last_name):
        return "Last name must contain letters only."
    if not re.match(EMAIL_PATTERN, email):
        return "Please use a valid @gmail.com address."
    return None


def normalized_scores(app):
    """Each criterion on a 0-100 scale (min-max normalization)."""
    return {
        "SAT": ((app.sat - 400) / 1200) * 100,
        "EC": (app.ec / 5) * 100,
        "GPA": (app.gpa / 4.0) * 100,
        "INT": (app.interview / 5) * 100,
        "REC": (app.recommendation / 5) * 100,
    }


def scholarship_tier(app):
    if app.sat >= 1550 and app.ec == 5 and app.gpa >= 3.9:
        return "Presidential Scholar (100%)"
    if app.sat >= 1450 or app.gpa >= 3.7:
        return "Merit Based (50%)"
    return "Standard"


class AdmissionEngine:
    def __init__(self):
        self.applicants = {}  # email -> Applicant

    def is_email_taken(self, email):  # REQ-02
        return email in self.applicants

    def calculate_rankings(self, weights=None):
        """Weighted multi-criteria score for every applicant (REQ-04)."""
        weights = weights or DEFAULT_WEIGHTS
        for app in self.applicants.values():
            scores = normalized_scores(app)
            app.total_score = sum(scores[key] * weights.get(key, 0.2) for key in scores)
            app.scholarship_status = scholarship_tier(app)

    def ranked(self):
        return sorted(self.applicants.values(), key=lambda a: a.total_score, reverse=True)
