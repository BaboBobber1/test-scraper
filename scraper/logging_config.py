import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


LOG_PATH = Path("logs")
LOG_PATH.mkdir(exist_ok=True)


def configure_logging(level: int = logging.INFO) -> None:
    """Configure application-wide logging with rotation.

    The logger records discovery steps, filter decisions, and enrichment outcomes
    to support observability during high-volume scraping runs.
    """

    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    handlers = []
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    handlers.append(stream_handler)

    file_handler = RotatingFileHandler(LOG_PATH / "scraper.log", maxBytes=5_000_000, backupCount=3)
    file_handler.setFormatter(formatter)
    handlers.append(file_handler)

    logging.basicConfig(level=level, handlers=handlers)


__all__ = ["configure_logging"]
