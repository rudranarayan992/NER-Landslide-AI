from __future__ import annotations

import logging
import sys
from typing import Optional

from .config import get_settings


def get_logger(name: Optional[str] = None) -> logging.Logger:
    settings = get_settings()
    logger = logging.getLogger(name or "ner_landslide_ai")
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))
    logger.propagate = False
    return logger
