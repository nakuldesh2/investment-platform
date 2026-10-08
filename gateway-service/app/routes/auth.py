"""Authentication routes for user registration, login, and token management"""

import logging
from fastapi import APIRouter, Depends, Response, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.config import GatewaySettings, get_settings
from app.db import get_db
from app.models import User
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, UserResponse
from app.utils.security import hash_password, verify_password, create_access_token, verify_token
from app.exceptions import InvalidRequestError, UnauthorizedError, DatabaseError
from app.logging_config import get_logger

router = APIRouter(prefix="/auth", tags=["auth"])
logger = get_logger(__name__)


def get_current_user_id(request: Request) -> int:
    """Extract user_id from request state (set by auth middleware)"""
    user_id = getattr(request.state, "user_id", None)
    if not user_id:
        raise UnauthorizedError("Not authenticated")
    return user_id


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(
    request: RegisterRequest,
    db: AsyncSession = Depends(get_db),
    settings: GatewaySettings = Depends(get_settings)
):
    """Register a new user account"""
    try:
        # Check if user already exists
        stmt = select(User).where(User.email == request.email)
        result = await db.execute(stmt)
        existing_user = result.scalar_one_or_none()

        if existing_user:
            logger.warning(f"Registration attempt with existing email: {request.email}")
            raise InvalidRequestError(f"Email {request.email} is already registered")

        # Check if email is in allowlist
        is_allowlisted = request.email in settings.allowlist_emails
        user_status = "approved" if is_allowlisted else "pending"

        # Create new user with hashed password
        new_user = User(
            email=request.email,
            password_hash=hash_password(request.password),
            is_allowlisted=is_allowlisted,
            status=user_status
        )
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        if is_allowlisted:
            logger.info(f"User registered and auto-approved: {new_user.email}")
        else:
            logger.info(f"User registered pending approval: {new_user.email}")

        return UserResponse(id=new_user.id, email=new_user.email)

    except InvalidRequestError:
        await db.rollback()
        raise
    except Exception as exc:
        await db.rollback()
        logger.error(f"Registration error: {str(exc)}", exc_info=True)
        raise DatabaseError("Failed to register user")


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
    settings: GatewaySettings = Depends(get_settings)
):
    """Authenticate user and return JWT token"""
    try:
        # Find user by email
        stmt = select(User).where(User.email == request.email)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        # Verify credentials
        if not user or not verify_password(request.password, user.password_hash):
            logger.warning(f"Failed login attempt for email: {request.email}")
            raise UnauthorizedError("Invalid email or password")

        # Check if user is allowlisted and approved
        if not user.is_allowlisted or user.status != "approved":
            logger.warning(f"Login attempt by non-approved user: {user.email} (status: {user.status})")
            raise UnauthorizedError("Your account is pending approval. Contact admin for access.")

        # Create JWT token
        token = create_access_token(user.id, settings)

        # Set token in httpOnly cookie
        response.set_cookie(
            key="access_token",
            value=token,
            httponly=True,
            secure=settings.is_production,
            samesite="strict",
            max_age=settings.jwt_expiration_hours * 3600
        )

        logger.info(f"User logged in successfully: {user.email}")
        return TokenResponse(access_token=token, token_type="bearer")

    except UnauthorizedError:
        raise
    except Exception as exc:
        logger.error(f"Login error: {str(exc)}", exc_info=True)
        raise UnauthorizedError("Login failed")


@router.post("/logout")
async def logout(response: Response):
    """Logout user by clearing token cookie"""
    response.delete_cookie(key="access_token", httponly=True)
    logger.info("User logged out")
    return {"message": "Logged out successfully"}


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: TokenResponse,
    response: Response,
    db: AsyncSession = Depends(get_db),
    settings: GatewaySettings = Depends(get_settings)
):
    """Refresh an expired JWT token"""
    try:
        # Verify old token to get user_id
        user_id = verify_token(request.access_token, settings)

        # Verify user still exists
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            raise UnauthorizedError("User not found")

        # Create new token
        new_token = create_access_token(user.id, settings)

        # Set new token in cookie
        response.set_cookie(
            key="access_token",
            value=new_token,
            httponly=True,
            secure=settings.is_production,
            samesite="strict",
            max_age=settings.jwt_expiration_hours * 3600
        )

        logger.info(f"Token refreshed for user: {user.email}")
        return TokenResponse(access_token=new_token, token_type="bearer")

    except UnauthorizedError:
        raise
    except Exception as exc:
        logger.error(f"Token refresh error: {str(exc)}", exc_info=True)
        raise UnauthorizedError("Failed to refresh token")


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Get current authenticated user information"""
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise UnauthorizedError("User not found")

    return UserResponse(id=user.id, email=user.email)


@router.get("/user-keys")
async def get_user_keys(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Get current user's stored API keys"""
    try:
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            raise UnauthorizedError("User not found")

        return {
            "user_id": user.id,
            "api_keys": user.api_keys or {}
        }

    except UnauthorizedError:
        raise
    except Exception as exc:
        logger.error(f"Error fetching user keys: {str(exc)}", exc_info=True)
        raise DatabaseError("Failed to fetch API keys")


@router.post("/user-keys")
async def update_user_keys(
    keys: dict,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Update current user's API keys"""
    try:
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            raise UnauthorizedError("User not found")

        # Update the user's API keys
        user.api_keys = keys
        await db.commit()
        await db.refresh(user)

        logger.info(f"API keys updated for user: {user.email} (keys: {list(keys.keys())})")

        return {
            "message": "API keys updated successfully",
            "user_id": user.id,
            "keys_stored": list(keys.keys())
        }

    except UnauthorizedError:
        await db.rollback()
        raise
    except Exception as exc:
        await db.rollback()
        logger.error(f"Error updating user keys: {str(exc)}", exc_info=True)
        raise DatabaseError("Failed to update API keys")
