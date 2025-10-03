#!/usr/bin/env python3
"""
Database initialization script for AIAlchemy
Run this to create tables and initialize the database
"""

import asyncio
import sys
import os

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.init_db_unified import init_database

async def main():
    """Main initialization function"""
    print("🔧 Initializing AIAlchemy database...")
    
    success = await init_database()
    
    if success:
        print("✅ Database initialization completed successfully!")
        sys.exit(0)
    else:
        print("❌ Database initialization failed!")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())