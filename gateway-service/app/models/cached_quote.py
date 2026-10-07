from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, Numeric, BigInteger, DateTime, Index
from app.db import Base


class CachedQuote(Base):
    """Cached stock quotes to reduce API calls"""
    __tablename__ = "cached_quotes"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), unique=True, nullable=False, index=True)
    price = Column(Numeric(10, 2), nullable=False)
    previous_close = Column(Numeric(10, 2), nullable=True)
    change_percent = Column(Numeric(5, 2), nullable=True)
    volume = Column(BigInteger, nullable=True)
    source = Column(String(50), nullable=False)
    cached_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False, default=lambda: datetime.utcnow() + timedelta(minutes=5))

    __table_args__ = (
        Index('idx_cached_quotes_expires_at', 'expires_at'),
    )

    def is_expired(self):
        return datetime.utcnow() > self.expires_at

    def __repr__(self):
        return f"<CachedQuote(symbol={self.symbol}, price={self.price})>"
