from __future__ import annotations

import re
from collections import Counter
from typing import Any

from textblob import TextBlob


_emotion_keywords = {
    "joy": {"happy", "grateful", "calm", "relieved", "good", "excited", "proud"},
    "sadness": {"sad", "lonely", "down", "empty", "crying", "hopeless", "tired"},
    "anxiety": {"anxious", "worried", "panic", "nervous", "overthinking", "fear"},
    "burnout": {"burnout", "exhausted", "drained", "overwhelmed", "deadline", "stuck"},
    "anger": {"angry", "frustrated", "annoyed", "upset", "irritated"},
    "motivation": {"focused", "motivated", "productive", "progress", "confident"},
}

_vader = None


def _get_vader():
    global _vader
    if _vader is not None:
        return _vader

    try:
        import nltk
        from nltk.sentiment import SentimentIntensityAnalyzer

        try:
            _vader = SentimentIntensityAnalyzer()
        except LookupError:
            nltk.download("vader_lexicon", quiet=True)
            _vader = SentimentIntensityAnalyzer()
    except Exception:
        _vader = False

    return _vader


def _emotion_breakdown(text: str) -> tuple[str, dict[str, int]]:
    tokens = re.findall(r"[a-zA-Z']+", text.lower())
    counts: Counter[str] = Counter()
    for token in tokens:
        for emotion, keywords in _emotion_keywords.items():
            if token in keywords:
                counts[emotion] += 1

    if not counts:
        return "balanced", {}
    emotion, _ = counts.most_common(1)[0]
    return emotion, dict(counts)


def analyze_text(text: str) -> dict[str, Any]:
    clean_text = text.strip()
    if not clean_text:
        return {
            "polarity": 0.0,
            "subjectivity": 0.0,
            "compound": 0.0,
            "sentiment_label": "neutral",
            "emotion": "balanced",
            "emotion_scores": {},
            "keywords_detected": [],
        }

    blob = TextBlob(clean_text)
    polarity = round(blob.sentiment.polarity, 3)
    subjectivity = round(blob.sentiment.subjectivity, 3)

    vader = _get_vader()
    if vader:
        compound = round(vader.polarity_scores(clean_text)["compound"], 3)
    else:
        compound = polarity

    if compound >= 0.2:
        sentiment_label = "positive"
    elif compound <= -0.2:
        sentiment_label = "negative"
    else:
        sentiment_label = "neutral"

    emotion, emotion_scores = _emotion_breakdown(clean_text)
    keywords_detected = sorted(
        {
            word
            for word in re.findall(r"[a-zA-Z']+", clean_text.lower())
            if any(word in keywords for keywords in _emotion_keywords.values())
        }
    )

    return {
        "polarity": polarity,
        "subjectivity": subjectivity,
        "compound": compound,
        "sentiment_label": sentiment_label,
        "emotion": emotion,
        "emotion_scores": emotion_scores,
        "keywords_detected": keywords_detected,
    }
