from __future__ import annotations

import argparse
import asyncio
import json
import logging
from pathlib import Path

from .connectors import StaticConnector
from .db import ensure_db
from .discovery import DiscoveryEngine
from .enrichment import enrich_channel
from .import_export import export_bundle, import_bundle
from .logging_config import configure_logging
from .settings import DiscoverySettings, EnrichmentSettings

HELP_TEXT = """
Mass discovery and enrichment engine for YouTube-scale scraping.

Features:
- Deep discovery that combines keyword search, related videos, and suggestion feeds.
- Robust filtering for language, subscriber thresholds, long-form video counts, and recency.
- Unified enrichment pipeline with identical settings for manual or automated runs.
- Email discovery with anti-spam pattern support and Telegram detection.
- SQLite-backed state persistence with automatic migrations and bundle import/export.
- Observability via structured logs of decisions, blacklisting, and extracted contacts.

Q&A:
- What qualifies as long-form? Non-short, non-live uploads that include metadata and publish dates.
- How are languages detected? A weighted heuristic uses titles, descriptions, tags, captions, audio, region, and recent videos.
- How do I avoid crashes on schema changes? Migrations run automatically on startup.
- How are deny languages stored? Internally as ISO-like uppercase codes (EN, DE, HI, TR).
- Can enrichment reuse settings? Yes. Manual and auto enrichment call the same enrichment function.

Common issues:
- Missing API credentials: ensure your connector implementation supplies channel/video metadata.
- Empty Telegram field: only populated when explicit Telegram references are detected.
- Email gate rejects channels: disable via settings.filters.email_gate_only when not required.

Technical notes:
- Discovery state, offsets, and counters are stored atomically in the discovery_state table.
- Future quality scores are supported by the quality_score column on channels.
"""


async def run_discovery(args: argparse.Namespace) -> None:
    configure_logging()
    db = ensure_db()
    settings = DiscoverySettings(
        queries=args.query,
        max_concurrency=args.concurrency,
    )
    sample_connector = StaticConnector([])
    engine = DiscoveryEngine(db, sample_connector, settings)
    await engine.discover()
    engine.persist_state()


def run_enrichment(args: argparse.Namespace) -> None:
    configure_logging()
    db = ensure_db()
    settings = EnrichmentSettings(email_mode=args.email_mode, language_mode=args.language_mode)
    channel = json.loads(Path(args.channel_json).read_text())
    videos = json.loads(Path(args.videos_json).read_text())
    enrich_channel(db, channel, videos, settings)


def main() -> None:
    parser = argparse.ArgumentParser(description="YouTube-scale discovery and enrichment tool")
    subparsers = parser.add_subparsers(dest="command")

    discovery_parser = subparsers.add_parser("discover", help="Run deep discovery")
    discovery_parser.add_argument("--query", action="append", default=[], help="Search query")
    discovery_parser.add_argument("--concurrency", type=int, default=10, help="Max concurrent tasks")
    discovery_parser.set_defaults(func=lambda args: asyncio.run(run_discovery(args)))

    enrich_parser = subparsers.add_parser("enrich", help="Enrich a channel using unified settings")
    enrich_parser.add_argument("--channel-json", required=True, help="Path to channel JSON")
    enrich_parser.add_argument("--videos-json", required=True, help="Path to videos JSON")
    enrich_parser.add_argument("--email-mode", choices=["description", "longform", "full"], default="full")
    enrich_parser.add_argument("--language-mode", choices=["fast", "precise"], default="precise")
    enrich_parser.set_defaults(func=run_enrichment)

    export_parser = subparsers.add_parser("export", help="Export bundle")
    export_parser.add_argument("--destination", required=True, help="Path to write data.json")
    export_parser.set_defaults(func=lambda args: export_bundle(ensure_db(), Path(args.destination)))

    import_parser = subparsers.add_parser("import", help="Import bundle")
    import_parser.add_argument("--source", required=True, help="Path to data.json")
    import_parser.set_defaults(func=lambda args: import_bundle(ensure_db(), Path(args.source)))

    help_parser = subparsers.add_parser("helpmodal", help="Show help modal content")
    help_parser.set_defaults(func=lambda args: print(HELP_TEXT))

    args = parser.parse_args()
    if not hasattr(args, "func"):
        parser.print_help()
        return
    args.func(args)


if __name__ == "__main__":
    main()
