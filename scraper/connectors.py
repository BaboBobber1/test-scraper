from __future__ import annotations

import asyncio
from typing import Any, AsyncGenerator, Iterable, Mapping


class StaticConnector:
    """A testing connector that returns pre-seeded discovery candidates."""

    def __init__(self, candidates: Iterable[Mapping[str, Any]]):
        self.candidates = list(candidates)

    async def search_channels(self, query: str) -> AsyncGenerator[Mapping[str, Any], None]:
        for candidate in self.candidates:
            await asyncio.sleep(0)
            yield candidate

    async def related_channels(self, video_id: str) -> AsyncGenerator[Mapping[str, Any], None]:
        for candidate in self.candidates:
            await asyncio.sleep(0)
            yield candidate

    async def suggest_channels(self, channel_id: str) -> AsyncGenerator[Mapping[str, Any], None]:
        for candidate in self.candidates:
            await asyncio.sleep(0)
            yield candidate


__all__ = ["StaticConnector"]
