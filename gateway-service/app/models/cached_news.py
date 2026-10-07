from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, Numeric, DateTime, Index
from app.db import Base


class CachedNews(Base):
    """Cached news sentiment scores"""
    __tablename__ = "cached_news"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), nullable=False, index=True)
    sentiment_score = Column(Numeric(3, 2), nullable=False)
    article_count = Column(Integer, nullable=False)
    cached_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False, default=lambda: datetime.utcnow() + timedelta(minutes=30))

    __table_args__ = (
        Index('idx_cached_news_symbol_cached_at', 'symbol', 'cached_at'),
        Index('idx_cached_news_expires_at', 'expires_at'),
    )

    def is_expired(self):
        return datetime.utcnow() > self.expires_at

    def __repr__(self):
        return f"<CachedNews(symbol={self.symbol}, sentiment={self.sentiment_score})>"
