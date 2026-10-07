"""Security utilities for authentication and password handling"""

import jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext
from app.config import GatewaySettings
from app.exceptions import UnauthorizedError

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password"""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(user_id: int, settings: GatewaySettings) -> str:
    """Create a JWT access token"""
    expire = datetime.utcnow() + timedelta(hours=settings.jwt_expiration_hours)
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    }
    token = jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)
    return token


def verify_token(token: str, settings: GatewaySettings) -> int:
    """Verify and decode a JWT token, returning the user_id"""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
        user_id = payload.get("sub")
        if not user_id:
            raise UnauthorizedError("Invalid token: no user ID")
        return int(user_id)
    except jwt.ExpiredSignatureError:
        raise UnauthorizedError("Token has expired")
    except jwt.InvalidTokenError:
        raise UnauthorizedError("Invalid token")
    except Exception as exc:
        raise UnauthorizedError(f"Token verification failed: {str(exc)}")
