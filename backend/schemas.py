from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class ChannelBase(BaseModel):
    youtube_channel_id: str
    name: Optional[str]
    url: Optional[str]
    subscribers: Optional[int]
    language: Optional[str]
    emails: Optional[str]
    telegram: Optional[str]
    status: str = "new"
    last_upload_at: Optional[datetime]
    last_checked_at: Optional[datetime]
    last_discovered_keyword: Optional[str]


class ChannelCreate(ChannelBase):
    pass


class ChannelRead(ChannelBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class DiscoveryStateRead(BaseModel):
    id: int
    keyword: str
    next_page_token: Optional[str]
    runs_count: int
    new_channels_found: int
    exhausted: bool
    last_run_at: Optional[datetime]
    video_no_new_pages: int

    class Config:
        orm_mode = True


class DiscoveryRequest(BaseModel):
    keywords: List[str]
    run_until_stopped: bool = True
    auto_enrich: bool = True
    min_subscribers: int = 1000
    min_longform_videos: int = 5
    max_last_upload_days: int = 30
    deny_languages: List[str] = []


class DiscoveryProgress(BaseModel):
    running: bool
    current_keyword: Optional[str]
    last_run_at: Optional[datetime]
    new_channels: int = 0


class EnrichSettings(BaseModel):
    email_enabled: bool = True
    email_mode: str = "FULL"
    language_enabled: bool = True
    language_mode: str = "PRECISE"
    refresh_channel_metadata: bool = True
    update_last_upload: bool = True


class EnrichmentRequest(BaseModel):
    channel_ids: Optional[List[int]] = None
    scope: str = "active"
    settings: EnrichSettings


class StatsResponse(BaseModel):
    total: int
    active: int
    blacklisted: int
    archived: int
    running_keyword: Optional[str]
    last_run_at: Optional[datetime]


class ChannelsQuery(BaseModel):
    status: Optional[str]
    language: Optional[str]
    has_email: bool = False
    has_telegram: bool = False
    min_subscribers: Optional[int]
    keyword: Optional[str]
    page: int = 1
    page_size: int = 25


class ImportBundle(BaseModel):
    data: list
    meta: dict
