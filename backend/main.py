import asyncio
from datetime import datetime
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from backend.config import Settings, get_settings
from backend.database import get_db, init_db
from backend.logging_config import logger
from backend.models import Channel, DiscoveryState, Setting
from backend.schemas import (
    ChannelsQuery,
    ChannelRead,
    DiscoveryProgress,
    DiscoveryRequest,
    EnrichSettings,
    EnrichmentRequest,
    ImportBundle,
    StatsResponse,
)
from backend.services.discovery import ensure_discovery_states, run_discovery_cycle
from backend.services.enrichment import enrich_channels
from backend.services.jobs import discovery_loop

app = FastAPI(title="Crypto YouTube Harvester")
settings = get_settings()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    await init_db()


@app.get("/api/stats", response_model=StatsResponse)
async def stats(db: AsyncSession = Depends(get_db)):
    total = (await db.execute(select(func.count(Channel.id)))).scalar()
    active = (await db.execute(select(func.count(Channel.id)).where(Channel.status == "active"))).scalar()
    blacklisted = (await db.execute(select(func.count(Channel.id)).where(Channel.status == "blacklisted"))).scalar()
    archived = (await db.execute(select(func.count(Channel.id)).where(Channel.status == "archived"))).scalar()
    return StatsResponse(
        total=total or 0,
        active=active or 0,
        blacklisted=blacklisted or 0,
        archived=archived or 0,
        running_keyword=discovery_loop.current_keyword if discovery_loop.running else None,
        last_run_at=None,
    )


@app.get("/api/channels", response_model=List[ChannelRead])
async def list_channels(
    status: Optional[str] = None,
    language: Optional[str] = None,
    has_email: bool = False,
    has_telegram: bool = False,
    min_subscribers: Optional[int] = None,
    keyword: Optional[str] = None,
    page: int = 1,
    page_size: int = 25,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Channel)
    if status:
        stmt = stmt.where(Channel.status == status)
    if language:
        stmt = stmt.where(Channel.language == language)
    if has_email:
        stmt = stmt.where(Channel.emails != None)
    if has_telegram:
        stmt = stmt.where(Channel.telegram != None)
    if min_subscribers:
        stmt = stmt.where(Channel.subscribers >= min_subscribers)
    if keyword:
        stmt = stmt.where(Channel.name.ilike(f"%{keyword}%"))
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(stmt)
    return result.scalars().all()


@app.post("/api/discovery/start")
async def start_discovery(payload: DiscoveryRequest, db: AsyncSession = Depends(get_db)):
    await ensure_discovery_states(db, payload.keywords)
    enrich_settings = EnrichSettings()
    asyncio.create_task(
        discovery_loop.start(
            db,
            payload.keywords,
            settings,
            enrich_settings,
            run_until_stopped=payload.run_until_stopped,
        )
    )
    return {"status": "started", "keywords": payload.keywords}


@app.post("/api/discovery/stop")
async def stop_discovery():
    discovery_loop.stop()
    return {"status": "stopped"}


@app.get("/api/discovery/progress", response_model=DiscoveryProgress)
async def discovery_progress():
    return DiscoveryProgress(
        running=discovery_loop.running,
        current_keyword=discovery_loop.current_keyword,
        last_run_at=None,
        new_channels=0,
    )


@app.post("/api/enrich/start")
async def start_enrichment(payload: EnrichmentRequest, db: AsyncSession = Depends(get_db)):
    if payload.scope == "active":
        stmt = await db.execute(select(Channel.id).where(Channel.status.in_(["new", "active"])))
        ids = [row[0] for row in stmt.all()]
    else:
        ids = payload.channel_ids or []
    result = await enrich_channels(db, ids, payload.settings)
    return {"status": "completed", "results": result}


@app.get("/api/settings/enrich")
async def get_enrich_settings(db: AsyncSession = Depends(get_db)):
    stmt = await db.execute(select(Setting).where(Setting.key == "enrich"))
    setting = stmt.scalars().first()
    return setting.value if setting else {}


@app.post("/api/settings/enrich")
async def save_enrich_settings(payload: EnrichSettings, db: AsyncSession = Depends(get_db)):
    stmt = await db.execute(select(Setting).where(Setting.key == "enrich"))
    setting = stmt.scalars().first()
    if not setting:
        setting = Setting(key="enrich", value=payload.json())
        db.add(setting)
    else:
        setting.value = payload.json()
    await db.commit()
    return {"status": "saved"}


@app.post("/api/import/bundle")
async def import_bundle(payload: ImportBundle, db: AsyncSession = Depends(get_db)):
    count = 0
    for row in payload.data:
        channel = Channel(**row)
        db.add(channel)
        count += 1
    await db.commit()
    return {"imported": count}


@app.get("/api/export/bundle")
async def export_bundle(db: AsyncSession = Depends(get_db)):
    channels = (await db.execute(select(Channel))).scalars().all()
    data = [ChannelRead.from_orm(ch).dict() for ch in channels]
    return {"data": data, "meta": {"exported_at": datetime.utcnow().isoformat()}}


@app.get("/api/health")
async def health():
    return {"status": "ok"}
