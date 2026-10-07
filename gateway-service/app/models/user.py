from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON
from app.db import Base


class User(Base):
    """User model for authentication, portfolio management, and API key management"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)

    # Allowlist fields
    is_allowlisted = Column(Boolean, default=False, nullable=False)
    status = Column(String(20), default="pending", nullable=False)  # pending, approved, denied

    # Email verification
    email_verified = Column(Boolean, default=False, nullable=False)
    verified_at = Column(DateTime, nullable=True)

    # API keys (encrypted storage - to be implemented)
    api_keys = Column(JSON, nullable=True)  # Structure: {"alpha_vantage": "...", "news_api": "...", "finnhub": "..."}

    # Approval tracking
    requested_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    approved_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, status={self.status})>"
