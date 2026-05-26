"""
Centralized logging module with rotating file handlers.
Provides consistent logging across the entire RAG application.
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from config import settings


def setup_logger(name: str, log_level: str = None) -> logging.Logger:
    """
    Setup a logger with both console and rotating file handlers.

    Args:
        name: Logger name (typically __name__)
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        Configured logger instance
    """
    if log_level is None:
        log_level = settings.log_level

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level))

    # Prevent duplicate handlers
    if logger.handlers:
        return logger

    # Create log directory if it doesn't exist
    log_path = Path(settings.log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # Formatter
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level))
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Rotating File Handler (10MB per file, 5 backup files)
    file_handler = RotatingFileHandler(
        filename=settings.log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(getattr(logging, log_level))
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


# Root logger for the application
app_logger = setup_logger("rag_app")
