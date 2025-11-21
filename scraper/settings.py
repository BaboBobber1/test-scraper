from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

DEFAULT_DENY_LANGUAGES = ["HI"]
DEFAULT_MIN_SUBSCRIBERS = 1000
DEFAULT_MIN_LONGFORM = 5
DEFAULT_MAX_LAST_UPLOAD_AGE_DAYS = 120


@dataclass
class LanguageGate:
    deny_languages: List[str] = field(default_factory=lambda: DEFAULT_DENY_LANGUAGES.copy())

    def normalized(self) -> List[str]:
        return [lang.upper() for lang in self.deny_languages]


@dataclass
class DiscoveryFilters:
    language_gate: LanguageGate = field(default_factory=LanguageGate)
    min_subscribers: int = DEFAULT_MIN_SUBSCRIBERS
    min_longform_videos: int = DEFAULT_MIN_LONGFORM
    max_last_upload_age_days: int = DEFAULT_MAX_LAST_UPLOAD_AGE_DAYS
    email_gate_only: bool = False


@dataclass
class EnrichmentSettings:
    email_mode: str = "full"  # description, longform, full
    language_mode: str = "precise"  # fast or precise
    telegram_detection: bool = True
    persist: bool = True


@dataclass
class DiscoverySettings:
    queries: List[str] = field(default_factory=list)
    filters: DiscoveryFilters = field(default_factory=DiscoveryFilters)
    enrichment: EnrichmentSettings = field(default_factory=EnrichmentSettings)
    max_concurrency: int = 10
    max_results_per_query: Optional[int] = None


__all__ = [
    "DiscoverySettings",
    "EnrichmentSettings",
    "DiscoveryFilters",
    "LanguageGate",
    "DEFAULT_DENY_LANGUAGES",
    "DEFAULT_MIN_SUBSCRIBERS",
]
