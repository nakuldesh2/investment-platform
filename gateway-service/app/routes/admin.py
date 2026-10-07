"""Admin endpoints for user management and allowlist approval"""

import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.config import GatewaySettings, get_settings
from app.db import get_db
from app.models import User
from app.logging_config import get_logger

router = APIRouter(prefix="/admin", tags=["admin"])
logger = get_logger(__name__)


async def verify_admin(user_id: int, settings: GatewaySettings) -> bool:
    """Verify if user is an admin (for future RBAC implementation)"""
    # For now, use ADMIN_EMAILS from settings
    # This should be replaced with proper role-based access control
    return True  # Placeholder


@router.get("/pending-users")
async def get_pending_users(
    db: AsyncSession = Depends(get_db),
    settings: GatewaySettings = Depends(get_settings)
):
    """Get list of pending user approval requests"""
    try:
        stmt = select(User).where(User.status == "pending").order_by(User.requested_at.desc())
        result = await db.execute(stmt)
        users = result.scalars().all()

        return {
            "pending_users": [
                {
                    "id": user.id,
                    "email": user.email,
                    "requested_at": user.requested_at.isoformat()
                }
                for user in users
            ]
        }
    except Exception as exc:
        logger.error(f"Error fetching pending users: {str(exc)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch pending users")


@router.post("/approve-user/{user_id}")
async def approve_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    settings: GatewaySettings = Depends(get_settings)
):
    """Approve a user for access"""
    try:
        # Find user
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if user.status != "pending":
            raise HTTPException(status_code=400, detail=f"User status is {user.status}, not pending")

        # Approve user
        user.status = "approved"
        user.is_allowlisted = True
        from datetime import datetime
        user.approved_at = datetime.utcnow()

        await db.commit()
        await db.refresh(user)

        logger.info(f"User approved: {user.email}")

        return {
            "message": "User approved",
            "user_id": user.id,
            "email": user.email,
            "status": user.status
        }
    except HTTPException:
        await db.rollback()
        raise
    except Exception as exc:
        await db.rollback()
        logger.error(f"Error approving user: {str(exc)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to approve user")


@router.post("/reject-user/{user_id}")
async def reject_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    settings: GatewaySettings = Depends(get_settings)
):
    """Reject a user access request"""
    try:
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if user.status != "pending":
            raise HTTPException(status_code=400, detail=f"User status is {user.status}, not pending")

        user.status = "denied"
        await db.commit()
        await db.refresh(user)

        logger.info(f"User rejected: {user.email}")

        return {
            "message": "User rejected",
            "user_id": user.id,
            "email": user.email,
            "status": user.status
        }
    except HTTPException:
        await db.rollback()
        raise
    except Exception as exc:
        await db.rollback()
        logger.error(f"Error rejecting user: {str(exc)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to reject user")


@router.post("/user/{user_id}/api-keys")
async def update_user_api_keys(
    user_id: int,
    api_keys: dict,
    db: AsyncSession = Depends(get_db),
):
    """Update user's API keys (encrypted)"""
    try:
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # In production, encrypt these keys using a proper encryption library
        # For now, store as-is (NOT RECOMMENDED FOR PRODUCTION)
        user.api_keys = api_keys

        await db.commit()
        await db.refresh(user)

        logger.info(f"API keys updated for user: {user.email}")

        return {
            "message": "API keys updated",
            "keys_stored": list(api_keys.keys())
        }
    except HTTPException:
        await db.rollback()
        raise
    except Exception as exc:
        await db.rollback()
        logger.error(f"Error updating API keys: {str(exc)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to update API keys")
