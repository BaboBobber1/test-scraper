from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy import event
from sqlalchemy.engine import Engine
import asyncio
from backend.config import get_settings

settings = get_settings()

engine = create_async_engine(settings.database_url, echo=False, future=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
Base = declarative_base()


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db():
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


def run_async(coro):
    return asyncio.get_event_loop().run_until_complete(coro)
