# Requirements

Written before the code, then traced to it. Each row has a test in `tests/test_admissions.py`
unless it is a UI-only rule.

| ID | Category | Requirement | Where it lives |
|---|---|---|---|
| REQ-01 | Identity | Every applicant gets a unique ID (UUID). | `Applicant.user_id` |
| REQ-02 | Validation | A second registration with the same email is blocked with a warning. | `AdmissionEngine.is_email_taken()` |
| REQ-03 | Self-service | Applicants have their own "Update Profile" tab. | `UniversityUI` → Update Profile tab |
| REQ-04 | Real-time | The ranking is recalculated whenever scores or weights change. | `AdmissionEngine.calculate_rankings()` |
| REQ-05 | Security | Only `@gmail.com` addresses are accepted (regex). | `validate_registration()` |
| REQ-06 | Audit | Every score change is logged with a timestamp. | `Applicant.audit_log` |
| REQ-07 | Business | Top applicants are tagged "Presidential Scholar"; strong ones get a merit tier. | `scholarship_tier()` |
| REQ-08 | Admin | Admins see all applicants as a ranked table. | Leaderboard tab (pandas DataFrame) |
| REQ-09 | UX | Applicants can delete their account. | `on_delete_click()` |
| REQ-10 | Integrity | SAT can't go outside 400–1600. | Slider bounds |
| REQ-11 | Event-driven | Every registration and update is sent to Kafka as a JSON event. | `AdmissionProducer.send_event()` |
| REQ-12 | Analysis | The recommendation score is read from the letter text, with strengths and missing traits. | `RecommendationAnalyzer` |

## Non-functional

- **Reliability:** a missing input never crashes the ranking; the app keeps working when no Kafka broker is running.
- **Usability:** registration and profile updates are separate tabs.
- **Performance target:** ranking a pool of 10,000 applicants should finish within 2 seconds.

## Example acceptance scenario (Gherkin)

```gherkin
Scenario: Invalid email is rejected
  Given an applicant on the registration tab
  When they enter "aybars@outlook.com" as their email
  Then the application is rejected with "Please use a valid @gmail.com address."
```
