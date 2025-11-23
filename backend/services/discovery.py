import asyncio
from datetime import datetime
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.config import Settings
from backend.logging_config import logger
from backend.models import Channel, DiscoveryState
from backend.scraper.youtube_search import search_channels


async def ensure_discovery_states(db: AsyncSession, keywords: List[str]):
    for kw in keywords:
        exists = await db.execute(select(DiscoveryState).where(DiscoveryState.keyword == kw))
        if not exists.scalars().first():
            db.add(DiscoveryState(keyword=kw, next_page_token=None, runs_count=0, new_channels_found=0))
    await db.commit()


async def run_discovery_cycle(db: AsyncSession, keyword: str, settings: Settings) -> dict:
    result = {"keyword": keyword, "new_channels": 0, "skipped": 0}
    channels, token = await search_channels(keyword)
    state_stmt = await db.execute(select(DiscoveryState).where(DiscoveryState.keyword == keyword))
    state = state_stmt.scalars().first()
    if not state:
        state = DiscoveryState(keyword=keyword)
        db.add(state)
    new_channel_ids = []
    for channel_id, name, url in channels:
        if not channel_id:
            continue
        existing_stmt = await db.execute(
            select(Channel).where(Channel.youtube_channel_id == channel_id)
        )
        if existing_stmt.scalars().first():
            result["skipped"] += 1
            continue
        channel = Channel(
            youtube_channel_id=channel_id,
            name=name,
            url=url,
            status="new",
            last_discovered_keyword=keyword,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(channel)
        new_channel_ids.append(channel_id)
        result["new_channels"] += 1
    state.next_page_token = token
    state.runs_count = (state.runs_count or 0) + 1
    state.last_run_at = datetime.utcnow()
    if result["new_channels"] == 0:
        state.video_no_new_pages = (state.video_no_new_pages or 0) + 1
    else:
        state.video_no_new_pages = 0
    state.new_channels_found = (state.new_channels_found or 0) + result["new_channels"]
    state.exhausted = state.video_no_new_pages >= 5
    await db.commit()
    logger.info("Discovery cycle %s new %s skipped %s", keyword, result["new_channels"], result["skipped"])
    return result
