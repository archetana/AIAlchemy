#!/usr/bin/env python3
"""
Standalone database initialization script for AIAlchemy
For use in startup.sh - no dependencies on external imports
"""

import asyncio
import sys
import os
import traceback
from datetime import datetime

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

async def standalone_init():
    """Initialize database with proper error handling"""
    try:
        print("🚀 Starting standalone database initialization...")
        
        # Import after path setup
        from app.init_db_unified import init_database
        
        success = await init_database()
        
        if success:
            print("✅ Standalone database initialization completed successfully!")
            return True
        else:
            print("⚠️ Standalone database initialization completed with warnings")
            return True  # Don't fail startup on warnings
        
    except Exception as e:
        print(f"❌ Standalone database initialization failed: {e}")
        traceback.print_exc()
        return True  # Don't fail startup, just warn

if __name__ == "__main__":
    result = asyncio.run(standalone_init())
    # Always exit 0 to not break startup process
    sys.exit(0)