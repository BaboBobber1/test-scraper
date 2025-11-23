import json
import random
import asyncio
import httpx
from typing import List, Tuple, Optional
from bs4 import BeautifulSoup
from backend.config import get_settings
from backend.logging_config import logger

settings = get_settings()


async def _fetch(url: str) -> str:
    async with httpx.AsyncClient(headers={"User-Agent": settings.user_agent}) as client:
        for attempt in range(3):
            try:
                resp = await client.get(url)
                if resp.status_code == 429:
                    await asyncio.sleep(1 + attempt)
                    continue
                resp.raise_for_status()
                await asyncio.sleep(random.uniform(0.5, 1.2))
                return resp.text
            except Exception as exc:
                logger.warning("search fetch failed %s", exc)
                await asyncio.sleep(1 + attempt)
        return ""


def _extract_initial_data(html: str) -> Optional[dict]:
    soup = BeautifulSoup(html, "html.parser")
    scripts = soup.find_all("script")
    for script in scripts:
        if script.string and "ytInitialData" in script.string:
            text = script.string
            marker = "var ytInitialData ="
            if marker in text:
                blob = text.split(marker, 1)[1]
                blob = blob.split(";\n", 1)[0]
                try:
                    return json.loads(blob)
                except Exception:
                    continue
    return None


def _walk_for_channels(data: dict) -> List[Tuple[str, str, str]]:
    channels = []
    if not data:
        return channels
    queue = [data]
    while queue:
        current = queue.pop()
        if isinstance(current, dict):
            if "channelId" in current and "title" in current:
                name = current.get("title")
                channel_id = current.get("channelId")
                url = f"https://www.youtube.com/channel/{channel_id}" if channel_id else None
                channels.append((channel_id, name, url))
            for value in current.values():
                queue.append(value)
        elif isinstance(current, list):
            queue.extend(current)
    return channels


async def search_channels(keyword: str) -> Tuple[List[Tuple[str, str, str]], Optional[str]]:
    url = f"https://www.youtube.com/results?search_query={httpx.QueryParams({'search_query': keyword})['search_query']}"
    html = await _fetch(url)
    data = _extract_initial_data(html)
    channels = _walk_for_channels(data)
    continuation = None
    try:
        contents = data["contents"]["twoColumnSearchResultsRenderer"]["primaryContents"][
            "sectionListRenderer"
        ]["contents"][0]["itemSectionRenderer"]["contents"]
        for block in contents:
            if "continuationItemRenderer" in block:
                continuation = (
                    block["continuationItemRenderer"]["continuationEndpoint"]["continuationCommand"][
                        "token"
                    ]
                )
                break
    except Exception:
        continuation = None
    return channels, continuation
