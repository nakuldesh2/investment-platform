from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, Numeric, DateTime, JSON, Index
from app.db import Base


class CachedSignal(Base):
    """Cached ML-generated trading signals"""
    __tablename__ = "cached_signals"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), unique=True, nullable=False, index=True)
    score = Column(Numeric(6, 4), nullable=False)
    confidence = Column(Numeric(5, 4), nullable=False)
    recommendation = Column(String(50), nullable=False)
    reason_codes = Column(JSON, default=list, nullable=False)
    cached_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False, default=lambda: datetime.utcnow() + timedelta(hours=1))

    __table_args__ = (
        Index('idx_cached_signals_expires_at', 'expires_at'),
    )

    def is_expired(self):
        return datetime.utcnow() > self.expires_at

    def __repr__(self):
        return f"<CachedSignal(symbol={self.symbol}, score={self.score}, recommendation={self.recommendation})>"
