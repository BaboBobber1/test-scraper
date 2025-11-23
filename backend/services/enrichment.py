from datetime import datetime
from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.logging_config import logger
from backend.models import Channel
from backend.scraper.email_extract import extract_emails_from_text
from backend.scraper.language_detect import detect_language_basic, detect_language_precise
from backend.scraper.telegram_extract import extract_telegram
from backend.scraper.youtube_channel import fetch_about, fetch_recent_videos
from backend.scraper.youtube_video import fetch_description
from backend.schemas import EnrichSettings


async def enrich_channels(db: AsyncSession, channel_ids: List[int], settings: EnrichSettings):
    results = []
    for channel_id in channel_ids:
        stmt = await db.execute(select(Channel).where(Channel.id == channel_id))
        channel = stmt.scalars().first()
        if not channel:
            continue
        try:
            if settings.refresh_channel_metadata:
                about = await fetch_about(channel.youtube_channel_id)
                if about:
                    channel.name = about.get("title") or channel.name
                    channel.emails = ",".join(about.get("emails", [])) or channel.emails
                    channel.telegram = about.get("telegram") or channel.telegram
                    if about.get("links"):
                        link_blob = " ".join(about["links"])
                        channel.emails = ",".join(
                            sorted(set((channel.emails or "").split(",") + extract_emails_from_text(link_blob)))
                        )
                        channel.telegram = channel.telegram or extract_telegram(link_blob)
            if settings.update_last_upload:
                videos = await fetch_recent_videos(channel.youtube_channel_id, limit=3)
                if videos:
                    channel.last_upload_at = max(v["published"] for v in videos)
            descriptions = []
            if settings.email_enabled:
                if settings.email_mode in ("FULL", "CHANNEL_ONLY"):
                    descriptions.append(channel.emails or "")
                if settings.email_mode in ("FULL", "VIDEOS_ONLY"):
                    videos = await fetch_recent_videos(channel.youtube_channel_id, limit=2)
                    for vid in videos:
                        desc = await fetch_description(vid["video_id"])
                        if desc:
                            descriptions.append(desc)
                emails = set((channel.emails or "").split(",")) if channel.emails else set()
                for text in descriptions:
                    emails.update(extract_emails_from_text(text))
                emails.discard("")
                channel.emails = ",".join(sorted(emails)) if emails else None
            if settings.language_enabled:
                texts = []
                if settings.language_mode == "BASIC":
                    texts = [channel.name or "", channel.emails or ""]
                    channel.language = detect_language_basic(texts)
                else:
                    videos = await fetch_recent_videos(channel.youtube_channel_id, limit=3)
                    texts = [channel.name or ""] + [v["title"] for v in videos]
                    channel.language = detect_language_precise(texts)
            channel.status = "active"
            channel.last_checked_at = datetime.utcnow()
            channel.updated_at = datetime.utcnow()
            await db.commit()
            results.append({"channel_id": channel_id, "status": "COMPLETED"})
        except Exception as exc:
            logger.exception("enrichment failed for %s", channel.youtube_channel_id)
            await db.rollback()
            results.append({"channel_id": channel_id, "status": "ERROR", "error": str(exc)})
    return results
