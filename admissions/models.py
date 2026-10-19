"""Data layer: one applicant and their audit log."""
import uuid
from datetime import datetime

from .analyzer import RecommendationAnalyzer


class Applicant:
    def __init__(self, first_name, last_name, email, sat, ec, gpa=3.0, interview=3, rec_text=""):
        self.user_id = str(uuid.uuid4())[:8]  # REQ-01: unique ID
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.sat = sat                  # 400 - 1600
        self.ec = ec                    # extracurricular impact, 1 - 5
        self.gpa = gpa                  # 0.0 - 4.0
        self.interview = interview      # 1 - 5

        # The recommendation score is read from the letter itself, not typed in
        self.rec_text = rec_text
        self.recommendation, self.strengths, self.weaknesses = RecommendationAnalyzer().analyze_letter(rec_text)

        self.total_score = 0.0
        self.scholarship_status = "Regular"  # REQ-07
        self.audit_log = []                  # REQ-06
        self.registration_date = datetime.now().strftime("%Y-%m-%d %H:%M")

        self.add_log(f"Account created. SAT: {sat}, EC: {ec}, GPA: {gpa}, INT: {interview}")
        self.add_log(f"Auto-evaluated rec letter score: {self.recommendation}/5")
        self.add_log(f"Detected strengths: {', '.join(self.strengths)}")
        self.add_log(f"Missing traits: {', '.join(self.weaknesses)}")

    def add_log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.audit_log.append(f"[{timestamp}] {message}")
