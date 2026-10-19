# Admissions Ranking System

A Python app that takes university applications, scores them on five criteria, ranks the
applicants with weights an admin can change live, and reads recommendation letters to score
them automatically.

Built in spring 2026 as a requirements-to-code project, mentored by Prof. Dr. Asım Egemen
Yılmaz (Ankara University, Electrical-Electronics Engineering).

## What it does

- **Registration** with validation: letters-only names, `@gmail.com` emails (regex), no duplicate accounts, SAT kept within 400–1600.
- **Weighted ranking:** SAT, GPA, extracurriculars, interview and recommendation are each normalized to 0–100, then combined with weights the admin sets with sliders. Changing the weights re-ranks everyone instantly.
- **Recommendation-letter analysis:** the letter's text is tokenized with scikit-learn's TF-IDF and scored 1–5 from positive and negative wording. It also lists the strengths the letter shows (leadership, technical skills, teamwork, creativity) and the ones it never mentions.
- **Scholarship tiers:** applicants are tagged Presidential Scholar, Merit Based or Standard.
- **Audit log:** every account change is timestamped.
- **Event streaming:** every registration and update is published to Kafka as JSON. The app keeps working without a broker.
- **Admin analytics:** a ranked table and a radar chart comparing the top applicants on all five criteria.

## How it's built

```
admissions/
  models.py    data layer: Applicant and its audit log
  engine.py    logic layer: validation, normalization, weighted ranking, scholarship rules
  analyzer.py  recommendation-letter scoring (scikit-learn TF-IDF)
  events.py    Kafka producer
  ui.py        ipywidgets interface: Registration, Update Profile, Leaderboard & Radar tabs
docs/requirements.md   requirements traced to code, plus an acceptance scenario
tests/                 one test per requirement
stress_test.py         command-line run with bad input and two ranking models
demo.ipynb             the app in a notebook (Jupyter or Google Colab)
```

The requirements were written first (functional and non-functional, each with testability
criteria) and every one is traced to the code that implements it in
[docs/requirements.md](docs/requirements.md).

## Run it

```bash
pip install -r requirements.txt
python stress_test.py      # validation and ranking demo in the terminal
pytest                     # the tests
jupyter notebook demo.ipynb  # the full interactive app
```

In Google Colab, upload the `admissions` folder and run `demo.ipynb`.

## Results

- All requirement tests pass.
- Ranking 10,000 applicants takes about 0.01 seconds (the target was under 2 seconds).
- The stress test shows the same three applicants swap order when the weights move from an academic-heavy model to a holistic one.
