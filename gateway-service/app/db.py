import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://investment_user:investment_pass@postgres:5432/investment_platform"
)

engine = create_async_engine(
    DATABASE_URL,
    poolclass=NullPool,
    echo=os.getenv("DATABASE_ECHO", "False").lower() == "true"
)

async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_fetch=False,
    autocommit=False,
    autoflush=False
)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models"""
    pass


async def get_db() -> AsyncSession:
    """Dependency injection for database session"""
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Initialize database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """Close database connection pool"""
    await engine.dispose()
