from pydantic import BaseSettings, Field
from typing import List


class Settings(BaseSettings):
    database_url: str = Field(default="sqlite+aiosqlite:///./harvester.db")
    cors_origins: List[str] = Field(default_factory=lambda: ["http://localhost:5173"])
    min_subscribers: int = 1000
    min_longform_videos: int = 5
    max_last_upload_days: int = 30
    deny_languages: List[str] = Field(default_factory=list)
    discovery_page_size: int = 5
    user_agent: str = (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
    )

    class Config:
        env_file = ".env"


def get_settings() -> Settings:
    return Settings()
