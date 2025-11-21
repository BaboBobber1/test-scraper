from __future__ import annotations

from pathlib import Path

from .db import Database


def export_bundle(db: Database, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    db.export_bundle(destination)


def import_bundle(db: Database, source: Path) -> None:
    db.import_bundle(source)


__all__ = ["export_bundle", "import_bundle"]
