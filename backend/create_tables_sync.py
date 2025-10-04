#!/usr/bin/env python3
"""
Synchronous table creation script for reliable database initialization
"""

import os
import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def create_tables_sync():
    """Create tables using synchronous SQLAlchemy (more reliable)"""
    try:
        print("🔧 Creating database tables synchronously...")
        
        # Import models to register them with Base
        from app import models
        from app.core.database import Base
        from sqlalchemy import create_engine
        
        # Get database URL and convert to sync if needed
        database_url = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./aialchemy.db")
        
        # Convert async URL to sync for table creation
        if "sqlite+aiosqlite" in database_url:
            sync_url = database_url.replace("sqlite+aiosqlite://", "sqlite:///")
        elif "postgresql+asyncpg" in database_url:
            sync_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
        else:
            sync_url = database_url
        
        print(f"📍 Using database URL: {sync_url}")
        
        # Create sync engine
        engine = create_engine(sync_url, echo=True)
        
        # Create all tables
        Base.metadata.create_all(engine)
        
        print("✅ Database tables created successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create tables: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = create_tables_sync()
    sys.exit(0 if success else 1)