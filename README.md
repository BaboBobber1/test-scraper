# YouTube-Scale Discovery & Enrichment Scraper

This repository provides a highly resilient foundation for mass scraping and enrichment of YouTube channels. The pipeline emphasizes deep discovery, database consistency, and unified enrichment settings.

## Highlights
- **Massive discovery**: architecture supports combining keyword search, related-video traversal, and suggestion feeds. Channels can be surfaced from titles, descriptions, tags, video metadata, and cross-video hints.
- **Resilience and migrations**: automatic SQLite migrations create every required table and store schema metadata to avoid crashes from missing columns or old databases.
- **Unified enrichment**: manual and automated enrichment share the same configuration and code paths, including email/Telegram extraction and language detection.
- **Filtering**: deny-language gating, subscriber thresholds, minimum long-form counts, upload recency checks, and optional email gate blacklisting.
- **Observability**: rotating logs plus structured database log entries capture discovery steps, filter triggers, and extracted contacts.
- **Import/Export**: portable bundle support for `data.json` and `meta.json` allows rebuilding or seeding databases.
- **Quality-score ready**: a `quality_score` column exists for future ranking without affecting current behavior.

## Quickstart
1. Create the environment (Python 3.11+ recommended).
2. Install any connector dependencies you need to call YouTube APIs.
3. Run discovery with your connector implementation wired into `DiscoveryEngine`.
4. Export data with `python -m scraper.cli export --destination data.json`.

## Help modal
Display the in-tool help content via:
```bash
python -m scraper.cli helpmodal
```
