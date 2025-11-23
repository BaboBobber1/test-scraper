import re
from typing import Optional

TELEGRAM_REGEX = re.compile(r"(?:https?://)?t\.me/([A-Za-z0-9_]{4,})", re.IGNORECASE)
HANDLE_REGEX = re.compile(r"@([A-Za-z0-9_]{4,})")


def extract_telegram(text: str) -> Optional[str]:
    if not text:
        return None
    url_match = TELEGRAM_REGEX.search(text)
    if url_match:
        return f"@{url_match.group(1)}"
    for handle_match in HANDLE_REGEX.finditer(text):
        handle = handle_match.group(1)
        if f"@{handle}" not in text or f"@{handle}" not in (text or ""):
            return f"@{handle}"
        return f"@{handle}"
    return None
