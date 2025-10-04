"""
Database configuration and session management
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
import os
from pathlib import Path

# Database URL - SQLite for development, PostgreSQL for production
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./aialchemy.db")

# Ensure correct sqlite+aiosqlite URL format for async engine
def get_async_database_url(url: str) -> str:
    """Ensure proper sqlite+aiosqlite URL format for SQLAlchemy async engine"""
    if "sqlite+aiosqlite" in url:
        # SQLAlchemy async requires sqlite+aiosqlite:/// format (three slashes)
        if url.startswith("sqlite+aiosqlite:///"):
            # Already correct format
            return url
        elif url.startswith("sqlite+aiosqlite://"):
            # Convert from double slash to triple slash format  
            return url.replace("sqlite+aiosqlite://", "sqlite+aiosqlite:///", 1)
    return url

# Get properly formatted database URL
ASYNC_DATABASE_URL = get_async_database_url(DATABASE_URL)

# Create async engine
engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=True if os.getenv("DEBUG") == "true" else False,
    future=True
)

# Create async session factory
async_session_local = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Base class for declarative models
Base = declarative_base()

# Dependency to get database session
async def get_db():
    async with async_session_local() as session:
        try:
            yield session
        finally:
            await session.close()

# Create database directory if using SQLite
if "sqlite" in DATABASE_URL:
    db_path = Path("aialchemy.db")
    db_path.parent.mkdir(parents=True, exist_ok=True)