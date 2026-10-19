"""Admission engine integration & stress test.

Runs from the command line: feeds bad and valid input through the engine and shows how
the ranking changes under two different weighting models.

    python stress_test.py
"""
from admissions import AdmissionEngine, Applicant, validate_registration

print("=" * 60)
print("🚀 STARTING AUTOMATED ADMISSION SYSTEM STRESS TEST")
print("=" * 60)

engine = AdmissionEngine()

# --- Test case 1: invalid and malicious input must be rejected ---
print("\n[TEST CASE 1] Invalid input validation...")
dirty_inputs = [
    {"fn": "John123", "ln": "Doe", "email": "john.doe@gmail.com"},
    {"fn": "Alice", "ln": "Smith!", "email": "alice@gmail.com"},
    {"fn": "Bob", "ln": "Marley", "email": "bob_marley@yahoo.com"},
    {"fn": "  ", "ln": "ValidLastName", "email": "hacker@gmail.com"},
]
for idx, payload in enumerate(dirty_inputs, 1):
    error = validate_registration(payload["fn"].strip(), payload["ln"].strip(), payload["email"].lower().strip())
    if error:
        print(f"❌ #{idx} rejected as expected: {error}")
    else:
        print(f"⚠️ #{idx} WARNING: unexpectedly passed validation!")

# --- Test case 2: seed valid applicants ---
print("\n" + "-" * 60)
print("[TEST CASE 2] Registering valid applicants...")
print("-" * 60)
valid_students = {
    "aybars.k@gmail.com": dict(first_name="Aybars", last_name="Kaya", sat=1580, ec=2, gpa=3.9, interview=5,
                               rec_text="An outstanding student who led our python coding team."),
    "mehmet.y@gmail.com": dict(first_name="Mehmet", last_name="Yilmaz", sat=1310, ec=5, gpa=3.4, interview=4,
                               rec_text="Excellent team captain, highly dedicated and creative."),
    "clara.s@gmail.com": dict(first_name="Clara", last_name="Oswald", sat=1460, ec=3, gpa=3.8, interview=3,
                              rec_text="A good student who sometimes struggled with deadlines."),
}
for email, data in valid_students.items():
    student = Applicant(email=email, **data)
    engine.applicants[email] = student
    print(f"✅ Registered: {student.first_name} {student.last_name} | ID: {student.user_id} "
          f"| Rec score: {student.recommendation}/5")

# --- Test case 3: same applicants, two weighting models ---
print("\n" + "-" * 60)
print("[TEST CASE 3] Ranking with custom weights")
print("-" * 60)
scenarios = {
    "📊 Scenario A (academic heavy)": {"SAT": 0.5, "EC": 0.05, "GPA": 0.3, "INT": 0.1, "REC": 0.05},
    "🎨 Scenario B (holistic / activity heavy)": {"SAT": 0.1, "EC": 0.4, "GPA": 0.1, "INT": 0.3, "REC": 0.1},
}
for name, weights in scenarios.items():
    print(f"\n{name}")
    engine.calculate_rankings(weights)
    for app in engine.ranked():
        print(f" - {app.first_name:<8}: Score = {app.total_score:.2f} | Scholarship = {app.scholarship_status}")

print("\n" + "=" * 60)
print("🏁 STRESS TEST COMPLETE")
print("=" * 60)
