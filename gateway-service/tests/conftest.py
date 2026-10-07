"""Pytest configuration and shared fixtures for gateway service tests"""

import pytest
import asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.main import app
from app.db import Base, get_db
from app.config import GatewaySettings
from app.utils.security import hash_password


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def db_engine():
    """Create in-memory SQLite database for testing"""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    await engine.dispose()


@pytest.fixture
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session"""
    async_session = async_sessionmaker(
        db_engine, class_=AsyncSession, expire_on_fetch=False
    )

    async with async_session() as session:
        yield session


@pytest.fixture
def test_settings():
    """Create test settings"""
    return GatewaySettings(
        environment="testing",
        debug=True,
        database_url="sqlite+aiosqlite:///:memory:",
        secret_key="test_secret_key_do_not_use_in_production",
        jwt_algorithm="HS256",
        jwt_expiration_hours=24,
    )


@pytest.fixture
def override_get_db(db_session):
    """Override get_db dependency with test session"""
    async def _override_get_db():
        yield db_session
    return _override_get_db


@pytest.fixture
def override_get_settings(test_settings):
    """Override get_settings dependency with test settings"""
    def _override_get_settings():
        return test_settings
    return _override_get_settings


@pytest.fixture
def client(override_get_db, override_get_settings):
    """Create test client with overridden dependencies"""
    from app.config import get_settings

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_settings] = override_get_settings

    with TestClient(app) as test_client:
        yield test_client

    # Clean up overrides
    app.dependency_overrides.clear()


@pytest.fixture
async def test_user(db_session):
    """Create a test user in the database"""
    from app.models import User

    test_user = User(
        email="testuser@example.com",
        password_hash=hash_password("testpassword123")
    )
    db_session.add(test_user)
    await db_session.commit()
    await db_session.refresh(test_user)
    return test_user


@pytest.fixture
def authenticated_client(client, test_user, test_settings):
    """Create authenticated test client with valid JWT token"""
    from app.utils.security import create_access_token

    token = create_access_token(test_user.id, test_settings)
    client.cookies.set("access_token", token)
    return client
