from __future__ import annotations

import re
from typing import Iterable, List, Set

EMAIL_PATTERN = re.compile(
    r"(?P<user>[\w.+-]+)\s*(?:@|\s+at\s+|\s*\[at\]\s*|\s*\(at\)\s*)\s*"
    r"(?P<domain>[\w.-]+)\s*(?:\.|\s+dot\s+|\s*\[dot\]\s*|\s*\(dot\)\s*)\s*"
    r"(?P<tld>[a-zA-Z]{2,})",
    re.IGNORECASE,
)


def extract_emails(blobs: Iterable[str]) -> List[str]:
    """Extract emails and anti-spam variants from text blobs."""

    seen: Set[str] = set()
    results: List[str] = []
    for blob in blobs:
        if not blob:
            continue
        for match in EMAIL_PATTERN.finditer(blob):
            email = f"{match.group('user')}@{match.group('domain')}.{match.group('tld')}"
            email_lower = email.lower()
            if email_lower not in seen:
                seen.add(email_lower)
                results.append(email_lower)
    return results


__all__ = ["extract_emails"]
