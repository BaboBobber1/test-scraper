from __future__ import annotations

import logging
from typing import Any, Iterable, Mapping

from .db import Database
from .email_parser import extract_emails
from .language_detection import detect_language
from .settings import EnrichmentSettings
from .telegram_detection import detect_telegram

LOGGER = logging.getLogger(__name__)


def enrich_channel(db: Database, channel: Mapping[str, Any], videos: Iterable[Mapping[str, Any]], settings: EnrichmentSettings) -> None:
    longform_videos = [v for v in videos if not v.get("is_short") and not v.get("is_live")]

    blobs = []
    if settings.email_mode in {"description", "full"}:
        blobs.append(channel.get("description", ""))
    if settings.email_mode in {"longform", "full"}:
        blobs.extend([v.get("description", "") for v in longform_videos])

    emails = extract_emails(blobs)

    language = detect_language(
        title=channel.get("title", ""),
        description=channel.get("description", ""),
        tags=channel.get("tags", []),
        channel_region=channel.get("region"),
        audio_language=channel.get("audio_language"),
        captions_language=channel.get("captions_language"),
        video_languages=[v.get("language_code") for v in longform_videos[:5] if v.get("language_code")],
        mode=settings.language_mode,
    )

    telegram = detect_telegram([
        channel.get("description", ""),
        channel.get("about", ""),
        *[v.get("description", "") for v in longform_videos],
    ]) if settings.telegram_detection else None

    payload = {
        "id": channel.get("id"),
        "title": channel.get("title"),
        "description": channel.get("description"),
        "subscriber_count": channel.get("subscriber_count"),
        "long_form_videos": len(longform_videos),
        "last_longform_upload": longform_videos[0].get("published_at") if longform_videos else None,
        "language_code": language,
        "emails": emails,
        "telegram": telegram,
    }
    db.upsert_channel(payload)
    db.bulk_insert_videos(videos)
    LOGGER.info("Enriched channel %s with %d emails", channel.get("id"), len(emails))


__all__ = ["enrich_channel"]
