"""
Database configuration and connection management for AIAlchemy.
Uses SQLAlchemy with async support for PostgreSQL.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool
import structlog

from app.core.config import get_settings
from app.core.exceptions import DatabaseError

logger = structlog.get_logger()


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


class DatabaseManager:
    """Database connection and session manager."""
    
    def __init__(self):
        self.engine = None
        self.async_session_maker = None
        self._is_connected = False
    
    async def connect(self) -> None:
        """Initialize database connection."""
        if self._is_connected:
            return
        
        settings = get_settings()
        
        try:
            # Create async engine with different config for SQLite vs PostgreSQL
            engine_kwargs = {
                "echo": settings.is_development,
                "future": True
            }
            
            # Only add pool settings for PostgreSQL (not SQLite)
            if not settings.database_url.startswith("sqlite"):
                engine_kwargs.update({
                    "pool_size": settings.database_pool_size,
                    "max_overflow": settings.database_max_overflow,
                    "poolclass": NullPool if settings.is_development else None,
                })
            else:
                # For SQLite, use NullPool to avoid connection pool issues
                engine_kwargs["poolclass"] = NullPool
            
            self.engine = create_async_engine(
                settings.database_url,
                **engine_kwargs
            )
            
            # Create session maker
            self.async_session_maker = async_sessionmaker(
                self.engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            # Test connection
            async with self.engine.begin() as conn:
                from sqlalchemy import text
                await conn.execute(text("SELECT 1"))
            
            self._is_connected = True
            logger.info("Database connection established", database_url=settings.database_url.split("@")[0])
            
        except Exception as e:
            logger.error("Failed to connect to database", error=str(e))
            raise DatabaseError(f"Failed to connect to database: {str(e)}")
    
    async def disconnect(self) -> None:
        """Close database connection."""
        if not self._is_connected:
            return
        
        try:
            if self.engine:
                await self.engine.dispose()
            
            self._is_connected = False
            logger.info("Database connection closed")
            
        except Exception as e:
            logger.error("Error closing database connection", error=str(e))
    
    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Get async database session with automatic cleanup.
        
        Usage:
            async with database_manager.get_session() as session:
                # Use session here
                result = await session.execute(query)
        """
        if not self._is_connected:
            raise DatabaseError("Database not connected")
        
        async with self.async_session_maker() as session:
            try:
                yield session
            except Exception as e:
                await session.rollback()
                logger.error("Database session error", error=str(e))
                raise DatabaseError(f"Database operation failed: {str(e)}")
            finally:
                await session.close()
    
    async def get_session_dependency(self) -> AsyncGenerator[AsyncSession, None]:
        """
        FastAPI dependency for getting database session.
        
        Usage:
            @app.get("/")
            async def endpoint(session: AsyncSession = Depends(database_manager.get_session_dependency)):
                # Use session here
        """
        async with self.get_session() as session:
            yield session
    
    @property
    def is_connected(self) -> bool:
        """Check if database is connected."""
        return self._is_connected


# Global database manager instance
database_manager = DatabaseManager()


# Dependency function for FastAPI
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency for database sessions.
    
    Usage:
        from app.core.database import get_db_session
        
        @router.get("/")
        async def get_items(db: AsyncSession = Depends(get_db_session)):
            # Use db session here
    """
    async with database_manager.get_session() as session:
        yield session