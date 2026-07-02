"""Test configuration and fixtures for white-box tests.

Uses an in-memory SQLite approach for unit tests where possible,
but the FTS and PostgreSQL-specific features require asyncpg.
These tests use a real PostgreSQL or SQLite-compatible patterns.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from netflix.config import settings
from netflix.main import create_app

# Check if a test database URL is configured
TEST_DATABASE_URL = getattr(settings, "test_database_url", None)


@pytest.fixture
def app():
    """Create the FastAPI app for testing."""
    return create_app()


@pytest_asyncio.fixture
async def session() -> AsyncGenerator[AsyncSession, None]:
    """Provide a test database session."""
    engine = create_async_engine(
        TEST_DATABASE_URL or settings.database_url,
        pool_pre_ping=True,
        echo=False,
    )
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    from netflix.models import Base

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with factory() as s:
        yield s

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()
