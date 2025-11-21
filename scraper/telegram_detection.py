from __future__ import annotations

import re
from typing import Iterable, Optional

TELEGRAM_PATTERN = re.compile(r"(?:t\.me/|https?://t\.me/)(?P<name>[A-Za-z0-9_]+)", re.IGNORECASE)
HANDLE_PATTERN = re.compile(r"(?<![\w@])@(?P<name>[A-Za-z0-9_]{4,})")


def detect_telegram(blobs: Iterable[str]) -> Optional[str]:
    for blob in blobs:
        if not blob:
            continue
        link_match = TELEGRAM_PATTERN.search(blob)
        if link_match:
            return f"t.me/{link_match.group('name')}"
        handle_match = HANDLE_PATTERN.search(blob)
        if handle_match and "@" + handle_match.group("name") not in blob.lower():
            return f"t.me/{handle_match.group('name')}"
    return None


__all__ = ["detect_telegram"]
