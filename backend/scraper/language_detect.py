from typing import List
from langdetect import detect


LANG_FALLBACK = "EN"


def detect_language_basic(texts: List[str]) -> str:
    combined = "\n".join(filter(None, texts))
    if not combined.strip():
        return LANG_FALLBACK
    try:
        return detect(combined)[:2].upper()
    except Exception:
        return LANG_FALLBACK


def detect_language_precise(texts: List[str]) -> str:
    # For demo purposes use same detector; placeholder for improved logic
    return detect_language_basic(texts)
