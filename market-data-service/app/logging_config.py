"""Structured logging configuration with correlation ID support"""

import logging
import os
import uuid
from contextvars import ContextVar
from pythonjsonlogger import jsonlogger


# Context variable to store correlation ID for request tracing
correlation_id: ContextVar[str] = ContextVar("correlation_id", default="")


class CorrelationIdFilter(logging.Filter):
    """Add correlation ID to all log records"""

    def filter(self, record):
        record.correlation_id = correlation_id.get() or str(uuid.uuid4())
        record.service_name = os.getenv("SERVICE_NAME", "investment-platform")
        return True


def setup_logging(service_name: str = "investment-platform"):
    """Configure structured JSON logging"""
    os.environ["SERVICE_NAME"] = service_name

    # Get root logger
    logger = logging.getLogger()
    logger.setLevel(os.getenv("LOG_LEVEL", "INFO"))

    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Create console handler with JSON formatter
    console_handler = logging.StreamHandler()
    json_formatter = jsonlogger.JsonFormatter(
        '%(timestamp)s %(level)s %(name)s %(message)s %(correlation_id)s %(service_name)s',
        timestamp=True
    )
    console_handler.setFormatter(json_formatter)

    # Add correlation ID filter
    console_handler.addFilter(CorrelationIdFilter())

    # Add handler to root logger
    logger.addHandler(console_handler)

    # Set library loggers to WARNING to reduce noise
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)

    return logger


def get_logger(name: str) -> logging.Logger:
    """Get logger instance for a module"""
    return logging.getLogger(name)
