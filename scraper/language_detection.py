from __future__ import annotations

import collections
from typing import Iterable, List, Mapping, Optional

LANGUAGE_HINTS = {
    "HI": {"hindi", "india", "हिंदी"},
    "EN": {"english", "uk", "us", "international"},
    "DE": {"german", "deutsch"},
    "TR": {"turkish", "türkçe"},
}


def _score_hint(haystack: str, lang: str) -> int:
    haystack_lower = haystack.lower()
    return sum(1 for keyword in LANGUAGE_HINTS.get(lang, set()) if keyword in haystack_lower)


def detect_language(
    title: str,
    description: str,
    tags: Iterable[str],
    channel_region: Optional[str] = None,
    audio_language: Optional[str] = None,
    captions_language: Optional[str] = None,
    video_languages: Optional[Iterable[str]] = None,
    mode: str = "precise",
) -> Optional[str]:
    """Detect language using multiple hints.

    A weighted approach considers titles, descriptions, tags, default audio language,
    caption language, channel region, and languages of the latest videos.
    """

    scores: collections.Counter[str] = collections.Counter()
    candidates = {"HI", "EN", "DE", "TR"}

    for lang in candidates:
        scores[lang] += _score_hint(title, lang)
        scores[lang] += _score_hint(description, lang)
        scores[lang] += sum(_score_hint(tag, lang) for tag in tags)

    for inferred in [channel_region, audio_language, captions_language]:
        if inferred:
            scores[inferred.upper()] += 2 if mode == "precise" else 1

    if video_languages:
        for lang in video_languages:
            scores[lang.upper()] += 2 if mode == "precise" else 1

    if not scores:
        return None

    top_lang, top_score = scores.most_common(1)[0]
    if top_score == 0:
        return None
    return top_lang


__all__ = ["detect_language"]
