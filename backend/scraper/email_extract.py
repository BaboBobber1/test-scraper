import re
from typing import List

EMAIL_REGEX = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")


ALT_REGEX = re.compile(
    r"([A-Za-z0-9._%+-]+)\s*\[?at\]?\s*([A-Za-z0-9.-]+)\s*\[?dot\]?\s*([A-Za-z]{2,})",
    re.IGNORECASE,
)


def extract_emails_from_text(text: str) -> List[str]:
    emails = set(match.group(0) for match in EMAIL_REGEX.finditer(text or ""))
    for alt in ALT_REGEX.finditer(text or ""):
        reconstructed = f"{alt.group(1)}@{alt.group(2)}.{alt.group(3)}"
        emails.add(reconstructed)
    return sorted(emails)
