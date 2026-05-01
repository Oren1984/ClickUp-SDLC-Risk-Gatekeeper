from __future__ import annotations

import logging
import sys


def setup_logging(log_level: str = "INFO") -> None:
    """
    Configure root logger with a structured format.

    Call once at application startup before any other module logs.
    Uses standard library logging only — no external frameworks.
    """
    level = getattr(logging, log_level.upper(), logging.INFO)

    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
        stream=sys.stdout,
        force=True,
    )
