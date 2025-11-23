from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.types import JSON
from sqlalchemy.sql import func
from backend.database import Base


class Channel(Base):
    __tablename__ = "channels"

    id = Column(Integer, primary_key=True, index=True)
    youtube_channel_id = Column(String, unique=True, nullable=False, index=True)
    name = Column(String)
    url = Column(String)
    subscribers = Column(Integer)
    language = Column(String)
    emails = Column(Text)
    telegram = Column(String)
    status = Column(String, default="new")
    last_upload_at = Column(DateTime)
    last_checked_at = Column(DateTime)
    last_discovered_keyword = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DiscoveryState(Base):
    __tablename__ = "discovery_state"

    id = Column(Integer, primary_key=True)
    keyword = Column(String, unique=True)
    next_page_token = Column(Text)
    runs_count = Column(Integer, default=0)
    new_channels_found = Column(Integer, default=0)
    exhausted = Column(Boolean, default=False)
    last_run_at = Column(DateTime)
    video_no_new_pages = Column(Integer, default=0)


class Setting(Base):
    __tablename__ = "settings"

    key = Column(String, primary_key=True)
    value = Column(Text)
