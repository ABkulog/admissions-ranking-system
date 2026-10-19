"""Recommendation-letter analysis: turns free text into a 1-5 score plus strengths and gaps."""
from sklearn.feature_extraction.text import TfidfVectorizer

POSITIVE_KEYWORDS = {
    "excellent", "outstanding", "great", "intelligent", "creative", "dedicated",
    "hardworking", "best", "highly", "impressed", "perfect", "success",
}
NEGATIVE_KEYWORDS = {"lazy", "late", "poor", "struggled", "weak", "unorganized", "difficult"}

# Trait categories and the words that signal them
TRAITS_LEXICON = {
    "Leadership": ["leadership", "led", "managed", "president", "organized", "captain"],
    "Technical Skills": ["coding", "programming", "python", "engineering", "math", "analytical", "science"],
    "Teamwork": ["team", "collaborative", "group", "helpful", "peer", "social"],
    "Creativity": ["creative", "art", "innovative", "design", "original", "painting"],
}


class RecommendationAnalyzer:
    def analyze_letter(self, text):
        """Return (score 1-5, strengths, missing traits) for a recommendation letter."""
        if not text or not text.strip():
            return 3, ["No traits detected"], ["No letter provided"]

        text_lower = text.lower()

        # Tokenize with TF-IDF so each distinct word counts once
        try:
            vectorizer = TfidfVectorizer(stop_words="english")
            vectorizer.fit_transform([text_lower])
            words = set(vectorizer.get_feature_names_out())
        except ValueError:  # the letter had only stop words
            words = set(text_lower.split())

        pos_count = len(words & POSITIVE_KEYWORDS)
        neg_count = len(words & NEGATIVE_KEYWORDS)

        # Start at 3, add for positive words, subtract for negative ones, keep within 1-5
        score = 3.0 + (pos_count * 0.5) - (neg_count * 1.0)
        final_score = int(max(1, min(5, round(score))))

        strengths = [trait for trait, keywords in TRAITS_LEXICON.items()
                     if any(kw in text_lower for kw in keywords)]
        if not strengths:
            strengths = ["General Competence"]

        # Traits the letter never mentions
        weaknesses = [trait for trait in TRAITS_LEXICON if trait not in strengths]
        if not weaknesses:
            weaknesses = ["None detected (well-rounded profile)"]

        return final_score, strengths, weaknesses
