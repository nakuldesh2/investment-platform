"""Global error handling middleware"""

import uuid
import logging
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from app.exceptions import ApplicationException
from app.logging_config import correlation_id, get_logger

logger = get_logger(__name__)


async def error_handling_middleware(request: Request, call_next):
    """
    Global error handling middleware that:
    1. Generates/propagates correlation ID for request tracing
    2. Catches application exceptions and returns standardized responses
    3. Logs errors with context
    """
    # Generate or extract correlation ID from request headers
    correlation_id_value = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
    correlation_id.set(correlation_id_value)

    try:
        response = await call_next(request)
        # Add correlation ID to response headers
        response.headers["X-Correlation-ID"] = correlation_id_value
        return response

    except ApplicationException as exc:
        # Log application exception
        logger.warning(
            f"{exc.__class__.__name__}: {exc.detail}",
            extra={"status_code": exc.status_code}
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.detail, "status_code": exc.status_code},
            headers={"X-Correlation-ID": correlation_id_value}
        )

    except HTTPException as exc:
        # Log HTTP exception
        logger.warning(
            f"HTTPException: {exc.detail}",
            extra={"status_code": exc.status_code}
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.detail, "status_code": exc.status_code},
            headers={"X-Correlation-ID": correlation_id_value}
        )

    except Exception as exc:
        # Log unexpected exceptions
        logger.error(
            f"Unexpected error: {type(exc).__name__}: {str(exc)}",
            exc_info=True
        )
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "status_code": 500,
                "correlation_id": correlation_id_value
            },
            headers={"X-Correlation-ID": correlation_id_value}
        )


def setup_error_handling(app):
    """Setup global error handling middleware for the FastAPI app"""
    app.middleware("http")(error_handling_middleware)
