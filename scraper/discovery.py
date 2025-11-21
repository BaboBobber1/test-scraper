from __future__ import annotations

import asyncio
import logging
from typing import Any, Iterable, List, Mapping, Optional, Set

from .db import Database
from .email_parser import extract_emails
from .filters import ChannelSnapshot, apply_filters
from .language_detection import detect_language
from .settings import DiscoverySettings
from .telegram_detection import detect_telegram

LOGGER = logging.getLogger(__name__)


class DiscoveryConnector:
    """Abstract connector for retrieving channel and video metadata."""

    async def search_channels(self, query: str) -> Iterable[Mapping[str, Any]]:
        raise NotImplementedError

    async def related_channels(self, video_id: str) -> Iterable[Mapping[str, Any]]:
        raise NotImplementedError

    async def suggest_channels(self, channel_id: str) -> Iterable[Mapping[str, Any]]:
        raise NotImplementedError


class DiscoveryEngine:
    def __init__(self, db: Database, connector: DiscoveryConnector, settings: DiscoverySettings):
        self.db = db
        self.connector = connector
        self.settings = settings
        self.state = db.load_discovery_state()

    async def discover(self) -> None:
        tasks = []
        for query in self.settings.queries:
            tasks.append(asyncio.create_task(self._discover_query(query)))
        if tasks:
            await asyncio.gather(*tasks)

    async def _discover_query(self, query: str) -> None:
        LOGGER.info("Starting discovery for query '%s'", query)
        limit = self.settings.max_results_per_query
        found_channels: Set[str] = set()
        async for candidate in self._bounded(self.connector.search_channels(query)):
            channel_id = candidate.get("id")
            if not channel_id or channel_id in found_channels:
                continue
            found_channels.add(channel_id)
            await self._handle_candidate(candidate)
            if limit and len(found_channels) >= limit:
                break

    async def _bounded(self, agen: Iterable[Mapping[str, Any]]):
        sem = asyncio.Semaphore(self.settings.max_concurrency)

        async def worker(item):
            async with sem:
                return item

        if hasattr(agen, "__aiter__"):
            async for item in agen:
                yield await worker(item)
        else:
            for item in agen:
                yield await worker(item)

    async def _handle_candidate(self, candidate: Mapping[str, Any]) -> None:
        channel_id = candidate.get("id")
        videos = candidate.get("videos", [])
        longform_videos = [v for v in videos if not v.get("is_short") and not v.get("is_live")]
        emails = extract_emails([
            candidate.get("description", ""),
            *[v.get("description", "") for v in longform_videos],
        ])
        telegram = None
        if self.settings.enrichment.telegram_detection:
            telegram = detect_telegram([
                candidate.get("description", ""),
                candidate.get("about", ""),
                *[v.get("description", "") for v in longform_videos],
            ])

        language = detect_language(
            title=candidate.get("title", ""),
            description=candidate.get("description", ""),
            tags=candidate.get("tags", []),
            channel_region=candidate.get("region"),
            audio_language=candidate.get("audio_language"),
            captions_language=candidate.get("captions_language"),
            video_languages=[v.get("language_code") for v in longform_videos[:5] if v.get("language_code")],
            mode=self.settings.enrichment.language_mode,
        )

        snapshot = ChannelSnapshot(
            subscriber_count=candidate.get("subscriber_count", 0),
            long_form_videos=len(longform_videos),
            last_longform_upload=(longform_videos[0].get("published_at") if longform_videos else None),
            language_code=language,
            emails=emails,
        )

        filter_result = apply_filters(self.settings.filters, snapshot)
        if not filter_result.accepted:
            LOGGER.info("Channel %s blacklisted: %s", channel_id, filter_result.reason)
            self.db.record_log("blacklist", {"channel_id": channel_id, "reason": filter_result.reason})
            self.db.upsert_channel(
                {
                    "id": channel_id,
                    "title": candidate.get("title"),
                    "description": candidate.get("description"),
                    "subscriber_count": candidate.get("subscriber_count"),
                    "long_form_videos": len(longform_videos),
                    "last_longform_upload": snapshot.last_longform_upload,
                    "language_code": language,
                    "blacklisted": 1,
                    "blacklist_reason": filter_result.reason,
                    "emails": emails,
                    "telegram": telegram,
                }
            )
            return

        LOGGER.info("Channel %s accepted for enrichment", channel_id)
        self.db.record_log("accepted", {"channel_id": channel_id})
        self.db.upsert_channel(
            {
                "id": channel_id,
                "title": candidate.get("title"),
                "description": candidate.get("description"),
                "subscriber_count": candidate.get("subscriber_count"),
                "long_form_videos": len(longform_videos),
                "last_longform_upload": snapshot.last_longform_upload,
                "language_code": language,
                "emails": emails,
                "telegram": telegram,
            }
        )
        if videos:
            self.db.bulk_insert_videos(videos)

    def persist_state(self) -> None:
        self.db.persist_discovery_state(self.state)


__all__ = ["DiscoveryConnector", "DiscoveryEngine"]
