"""JWT authentication middleware for validating protected endpoints"""

import logging
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.utils.security import verify_token
from app.exceptions import UnauthorizedError
from app.logging_config import get_logger

logger = get_logger(__name__)

# Public endpoints that don't require authentication
PUBLIC_PATHS = {
    "/health",
    "/auth/register",
    "/auth/login",
    "/auth/refresh",
    "/openapi.json",
    "/docs",
    "/redoc",
}


async def jwt_middleware(request: Request, call_next):
    """
    JWT validation middleware that:
    1. Checks if the endpoint requires authentication
    2. Extracts JWT from cookie or Authorization header
    3. Validates token and extracts user_id
    4. Adds user_id to request state for endpoints to use
    """
    # Check if path is public
    path = request.url.path
    if any(path.startswith(public) for public in PUBLIC_PATHS):
        return await call_next(request)

    try:
        # Extract token from cookie or Authorization header
        token = None

        # Try cookie first (httpOnly cookie)
        token = request.cookies.get("access_token")

        # Fall back to Authorization header
        if not token:
            auth_header = request.headers.get("Authorization", "")
            if auth_header.startswith("Bearer "):
                token = auth_header[7:]  # Remove "Bearer " prefix

        if not token:
            logger.warning(f"Missing token for protected endpoint: {path}")
            return JSONResponse(
                status_code=401,
                content={"error": "Unauthorized", "detail": "Missing authentication token"}
            )

        # Verify token
        settings = get_settings()
        user_id = verify_token(token, settings)

        # Add user_id to request state for use in endpoints
        request.state.user_id = user_id

        response = await call_next(request)
        return response

    except UnauthorizedError as exc:
        logger.warning(f"Unauthorized access attempt to {path}: {exc.detail}")
        return JSONResponse(
            status_code=401,
            content={"error": "Unauthorized", "detail": exc.detail}
        )
    except Exception as exc:
        logger.error(f"Authentication error for {path}: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=401,
            content={"error": "Unauthorized", "detail": "Authentication failed"}
        )


def get_current_user_id(request: Request) -> int:
    """Dependency to get current user ID from request state"""
    user_id = getattr(request.state, "user_id", None)
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user_id
