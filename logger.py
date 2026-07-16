"""Logging helpers for SlapPC."""

from __future__ import annotations

import logging
from pathlib import Path


def configure_logging(base_dir: str) -> logging.Logger:
    """Configure file and console logging for the application."""
    log_path = Path(base_dir) / "debug.log"

    logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(log_path, mode="w", encoding="utf-8", delay=True),
            logging.StreamHandler(),
        ],
    )
    return logging.getLogger("SlapPC")
