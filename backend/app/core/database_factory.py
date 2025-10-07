"""
Database Factory
Automatically chooses between SQLAlchemy and Supabase based on configuration
"""

import os
import logging
from typing import Optional, AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import database_manager
from app.services.database_service import db_service

logger = logging.getLogger(__name__)

class DatabaseFactory:
    """Factory for database operations that automatically routes to correct backend"""
    
    def __init__(self):
        self.settings = get_settings()
        self._initialized = False
    
    async def initialize(self):
        """Initialize the appropriate database backend"""
        if self._initialized:
            return
        
        # Log current configuration
        logger.info("🔧 Database Factory Initialization")
        logger.info(f"   Environment: {self.settings.environment}")
        logger.info(f"   Supabase URL: {'✅ Set' if self.settings.supabase_url else '❌ Not Set'}")
        logger.info(f"   Supabase Key: {'✅ Set' if self.settings.supabase_anon_key else '❌ Not Set'}")
        logger.info(f"   USE_SUPABASE: {self.settings.use_supabase}")
        logger.info(f"   Should Use Supabase: {self.settings.should_use_supabase}")
        
        if self.settings.should_use_supabase:
            logger.info("🚀 Using Supabase as primary database")
            # Ensure database service uses Supabase
            db_service.use_supabase = True
            
            # Test Supabase connection
            try:
                from app.core.supabase_client import get_supabase_client
                supabase = get_supabase_client()
                
                # Test basic query
                result = supabase.table('users').select('count').limit(1).execute()
                logger.info("✅ Supabase connection verified")
                
            except Exception as e:
                logger.error(f"❌ Supabase connection failed: {e}")
                logger.info("🔄 Falling back to SQLAlchemy")
                
                # Fallback to SQLAlchemy
                await database_manager.connect()
                db_service.use_supabase = False
        else:
            logger.info("🗄️ Using SQLAlchemy as primary database")
            await database_manager.connect()
            db_service.use_supabase = False
        
        self._initialized = True
    
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get database session (only for SQLAlchemy operations)"""
        if not self._initialized:
            await self.initialize()
        
        if self.settings.should_use_supabase:
            # For Supabase, we don't use SQLAlchemy sessions
            # This should only be called for legacy SQLAlchemy operations
            logger.warning("⚠️ SQLAlchemy session requested but using Supabase")
            # Return a dummy session or raise an error
            raise RuntimeError("SQLAlchemy session not available when using Supabase")
        
        async with database_manager.get_session() as session:
            yield session
    
    @property
    def is_using_supabase(self) -> bool:
        """Check if currently using Supabase"""
        return self.settings.should_use_supabase
    
    def get_database_info(self) -> dict:
        """Get information about current database configuration"""
        return {
            "backend": "Supabase" if self.settings.should_use_supabase else "SQLAlchemy",
            "database_url": self.settings.database_url if not self.settings.should_use_supabase else f"supabase://{self.settings.supabase_url}",
            "environment": self.settings.environment,
            "auto_detected": not self.settings.use_supabase and self.settings.should_use_supabase,
            "connection_status": "connected" if self._initialized else "not_initialized"
        }

# Global factory instance
database_factory = DatabaseFactory()

async def init_database():
    """Initialize database with automatic backend selection"""
    await database_factory.initialize()
    return True

async def get_db_info():
    """Get database information"""
    return database_factory.get_database_info()