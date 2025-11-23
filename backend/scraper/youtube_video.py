import asyncio
import json
import random
from typing import Optional

import httpx
from bs4 import BeautifulSoup

from backend.config import get_settings
from backend.logging_config import logger

settings = get_settings()


async def fetch_description(video_id: str) -> Optional[str]:
    url = f"https://www.youtube.com/watch?v={video_id}"
    async with httpx.AsyncClient(headers={"User-Agent": settings.user_agent}) as client:
        for attempt in range(3):
            try:
                resp = await client.get(url)
                if resp.status_code == 429:
                    await asyncio.sleep(1 + attempt)
                    continue
                resp.raise_for_status()
                soup = BeautifulSoup(resp.text, "html.parser")
                for script in soup.find_all("script"):
                    if script.string and "ytInitialPlayerResponse" in script.string:
                        text = script.string
                        marker = "var ytInitialPlayerResponse ="
                        if marker in text:
                            blob = text.split(marker, 1)[1].split(";\n", 1)[0]
                            data = json.loads(blob)
                            desc = (
                                data.get("videoDetails", {})
                                .get("shortDescription", "")
                                .replace("\\n", "\n")
                            )
                            await asyncio.sleep(random.uniform(0.3, 0.6))
                            return desc
            except Exception as exc:
                logger.warning("video fetch failed %s", exc)
                await asyncio.sleep(1 + attempt)
        return None
