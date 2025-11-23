import asyncio
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.config import Settings
from backend.logging_config import logger
from backend.models import Channel, DiscoveryState
from backend.schemas import EnrichSettings
from backend.services.discovery import run_discovery_cycle
from backend.services.enrichment import enrich_channels


class DiscoveryLoop:
    def __init__(self):
        self._task: Optional[asyncio.Task] = None
        self.running = False
        self.current_keyword: Optional[str] = None
        self.auto_enrich: bool = True
        self.settings: Optional[Settings] = None
        self.enrich_settings: Optional[EnrichSettings] = None

    def stop(self):
        self.running = False
        if self._task:
            self._task.cancel()

    async def start(
        self,
        db: AsyncSession,
        keywords: List[str],
        settings: Settings,
        enrich_settings: EnrichSettings,
        run_until_stopped: bool = True,
    ):
        self.running = True
        self.settings = settings
        self.enrich_settings = enrich_settings
        while self.running:
            for kw in keywords:
                self.current_keyword = kw
                result = await run_discovery_cycle(db, kw, settings)
                if result.get("new_channels") and self.auto_enrich:
                    # enrich newly added channels (status new)
                    stmt = await db.execute(
                        select(Channel.id).where(Channel.last_discovered_keyword == kw)
                    )
                    ids = [row[0] for row in stmt.all()]
                    await enrich_channels(db, ids, enrich_settings)
                await asyncio.sleep(0.5)
                if not run_until_stopped:
                    self.running = False
                    break
            await asyncio.sleep(1)


discovery_loop = DiscoveryLoop()
