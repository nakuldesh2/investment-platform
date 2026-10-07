import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
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


async def get_db() -> AsyncSession:
    """Dependency injection for database session"""
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


async def close_db():
    """Close database connection pool"""
    await engine.dispose()
