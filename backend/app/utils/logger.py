"""
Structured logging configuration for the Sonus backend.

Provides JSON-formatted log output with consistent fields
for structured log aggregation and analysis.
"""

import logging
import sys
from datetime import datetime, timezone

from app.config.settings import get_settings


class StructuredFormatter(logging.Formatter):
    """Emits log records as structured key=value lines for easy parsing."""

    def format(self, record: logging.LogRecord) -> str:
        timestamp = datetime.now(timezone.utc).isoformat()
        level = record.levelname
        logger_name = record.name
        message = record.getMessage()

        base = f"ts={timestamp} level={level} logger={logger_name} msg=\"{message}\""

        # Append any extra fields attached to the record
        if hasattr(record, "extra_fields"):
            extras = " ".join(f"{k}={v}" for k, v in record.extra_fields.items())
            base = f"{base} {extras}"

        if record.exc_info and not record.exc_text:
            record.exc_text = self.formatException(record.exc_info)
        if record.exc_text:
            base = f"{base}\n{record.exc_text}"

        return base


def setup_logging() -> logging.Logger:
    """
    Configure the root 'sonus' logger.

    Call once at application startup.  All modules should use
    ``logging.getLogger("sonus.<module>")`` to inherit this config.
    """
    settings = get_settings()

    logger = logging.getLogger("sonus")
    logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))

    # Avoid duplicate handlers on repeated calls
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(StructuredFormatter())
        logger.addHandler(handler)

    # Silence noisy third-party loggers
    for noisy in ("chromadb", "httpx", "httpcore", "neo4j"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    return logger


def get_logger(name: str) -> logging.Logger:
    """Return a child logger under the 'sonus' namespace."""
    return logging.getLogger(f"sonus.{name}")
