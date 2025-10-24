# app/config/logging_config.py
import logging
import sys
from logging.handlers import RotatingFileHandler

LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"

def setup_logging(log_level: str = "INFO"):
    """Configure global logging for FastAPI."""
    # Root logger
    logger = logging.getLogger()
    logger.setLevel(log_level)

    # Remove existing handlers to avoid duplicates in reloads
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Console handler (stdout for Docker/Kubernetes)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT))

    # File handler (rotates daily / per size)
    file_handler = RotatingFileHandler(
        "logs/app.log", maxBytes=5_000_000, backupCount=3, encoding="utf-8"
    )
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT))

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    # Silence noisy loggers (optional)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)

    return logger
