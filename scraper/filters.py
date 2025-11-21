from __future__ import annotations

import datetime as dt
import logging
from dataclasses import dataclass
from typing import Mapping, Optional

from .settings import DiscoveryFilters

LOGGER = logging.getLogger(__name__)


@dataclass
class FilterResult:
    accepted: bool
    reason: Optional[str] = None


@dataclass
class ChannelSnapshot:
    subscriber_count: int
    long_form_videos: int
    last_longform_upload: Optional[str]
    language_code: Optional[str]
    emails: list[str]


DEFAULT_NOW = dt.datetime.utcnow


def apply_filters(filters: DiscoveryFilters, snapshot: ChannelSnapshot, now_factory=DEFAULT_NOW) -> FilterResult:
    deny_langs = {code.upper() for code in filters.language_gate.normalized()}
    if snapshot.language_code and snapshot.language_code.upper() in deny_langs:
        reason = f"Language {snapshot.language_code} denied"
        LOGGER.debug(reason)
        return FilterResult(False, reason)

    if snapshot.subscriber_count is not None and snapshot.subscriber_count < filters.min_subscribers:
        reason = f"Subscribers below threshold: {snapshot.subscriber_count} < {filters.min_subscribers}"
        LOGGER.debug(reason)
        return FilterResult(False, reason)

    if snapshot.long_form_videos < filters.min_longform_videos:
        reason = f"Insufficient long-form videos: {snapshot.long_form_videos} < {filters.min_longform_videos}"
        LOGGER.debug(reason)
        return FilterResult(False, reason)

    if filters.max_last_upload_age_days is not None:
        if not snapshot.last_longform_upload:
            reason = "No long-form upload date"
            LOGGER.debug(reason)
            return FilterResult(False, reason)
        try:
            published = dt.datetime.fromisoformat(snapshot.last_longform_upload)
            if (now_factory() - published).days > filters.max_last_upload_age_days:
                reason = (
                    f"Last upload too old: {(now_factory() - published).days}d > "
                    f"{filters.max_last_upload_age_days}d"
                )
                LOGGER.debug(reason)
                return FilterResult(False, reason)
        except ValueError:
            reason = "Invalid long-form upload timestamp"
            LOGGER.debug(reason)
            return FilterResult(False, reason)

    if filters.email_gate_only and not snapshot.emails:
        reason = "Email gate enabled but no emails present"
        LOGGER.debug(reason)
        return FilterResult(False, reason)

    return FilterResult(True)


__all__ = ["apply_filters", "ChannelSnapshot", "FilterResult"]
