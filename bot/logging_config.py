"""
Logging configuration module for the trading bot.

Provides centralized logging setup with both file and console handlers,
ensuring all application events are properly logged with timestamps and levels.
"""

import logging
import os
import sys
from logging.handlers import RotatingFileHandler

from bot import config


def setup_logging(
    log_level: str | None = None,
    log_file_path: str | None = None
) -> logging.Logger:
    """
    Configure and initialize the application logging system.

    Creates a logs directory if it doesn't exist, sets up a rotating
    file handler, and a console handler with proper formatting.

    Args:
        log_level: Override the default log level. Defaults to config.LOG_LEVEL.
        log_file_path: Override the default log file path.
                       Defaults to config.LOG_FILE_PATH.

    Returns:
        logging.Logger: Configured root logger for the application.

    Example:
        >>> logger = setup_logging()
        >>> logger.info("Application started")
    """
    # Determine log level and file path
    level = (log_level or config.LOG_LEVEL).upper()
    log_path = log_file_path or config.LOG_FILE_PATH

    # Create logs directory if it doesn't exist
    log_dir = os.path.dirname(log_path)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)

    # Get the root logger for our application
    logger = logging.getLogger("trading_bot")
    logger.setLevel(getattr(logging, level, logging.INFO))

    # Clear existing handlers to avoid duplicates on re-initialization
    logger.handlers.clear()

    # Define log format
    formatter = logging.Formatter(
        fmt=config.LOG_FORMAT,
        datefmt=config.LOG_DATE_FORMAT
    )

    # File handler with rotation (max 5MB per file, keep 3 backups)
    try:
        file_handler = RotatingFileHandler(
            filename=log_path,
            maxBytes=5_242_880,  # 5 MB
            backupCount=3,
            encoding="utf-8"
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except OSError as e:
        # If we can't create the log file, log to stderr as fallback
        print(
            f"Warning: Could not create log file at {log_path}: {e}",
            file=sys.stderr
        )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger
