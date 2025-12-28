# veridian_atlas/utils/logger.py

import logging
from logging import Logger

LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def get_logger(name: str) -> Logger:
    logger = logging.getLogger(name)

    # Avoid duplicate handlers if logger already configured
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))
    logger.addHandler(handler)

    # Prevent double logging caused by root handler propagation
    logger.propagate = False

    return logger
