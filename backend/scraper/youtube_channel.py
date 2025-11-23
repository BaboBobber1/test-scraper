import asyncio
import random
from datetime import datetime
from typing import Dict, List, Optional

import httpx
from bs4 import BeautifulSoup

from backend.config import get_settings
from backend.logging_config import logger
from backend.scraper.email_extract import extract_emails_from_text
from backend.scraper.telegram_extract import extract_telegram

settings = get_settings()


async def fetch_about(channel_id: str) -> Dict:
    url = f"https://www.youtube.com/channel/{channel_id}/about"
    async with httpx.AsyncClient(headers={"User-Agent": settings.user_agent}) as client:
        for attempt in range(3):
            try:
                resp = await client.get(url)
                if resp.status_code == 429:
                    await asyncio.sleep(1 + attempt)
                    continue
                resp.raise_for_status()
                soup = BeautifulSoup(resp.text, "html.parser")
                title = soup.title.string if soup.title else None
                description = " ".join(
                    [meta.get("content") for meta in soup.find_all("meta", {"name": "description"})]
                )
                links = [a.get("href") for a in soup.find_all("a", href=True)]
                emails = extract_emails_from_text(resp.text + " " + description)
                telegram = extract_telegram(" ".join(links) + " " + description)
                await asyncio.sleep(random.uniform(0.3, 0.8))
                return {
                    "title": title,
                    "description": description,
                    "links": links,
                    "emails": emails,
                    "telegram": telegram,
                }
            except Exception as exc:
                logger.warning("about scrape failed: %s", exc)
                await asyncio.sleep(1 + attempt)
        return {}


async def fetch_recent_videos(channel_id: str, limit: int = 5) -> List[Dict]:
    url = f"https://www.youtube.com/channel/{channel_id}/videos"
    async with httpx.AsyncClient(headers={"User-Agent": settings.user_agent}) as client:
        try:
            resp = await client.get(url)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            scripts = soup.find_all("script")
            videos = []
            for script in scripts:
                if script.string and "ytInitialData" in script.string:
                    text = script.string
                    marker = "var ytInitialData ="
                    if marker in text:
                        blob = text.split(marker, 1)[1].split(";\n", 1)[0]
                        # naive parse for videoRenderer
                        import json

                        data = json.loads(blob)
                        queue = [data]
                        while queue and len(videos) < limit:
                            cur = queue.pop()
                            if isinstance(cur, dict):
                                if cur.get("videoId") and cur.get("title"):
                                    published = datetime.utcnow()
                                    videos.append(
                                        {
                                            "video_id": cur.get("videoId"),
                                            "title": cur.get("title", {}).get("runs", [{}])[0].get("text"),
                                            "published": published,
                                            "is_short": cur.get("isShort", False),
                                        }
                                    )
                                queue.extend(cur.values())
                            elif isinstance(cur, list):
                                queue.extend(cur)
                    break
            await asyncio.sleep(random.uniform(0.3, 0.8))
            return videos[:limit]
        except Exception as exc:
            logger.warning("video scrape failed %s", exc)
            return []
