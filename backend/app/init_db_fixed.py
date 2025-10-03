"""
Fixed database initialization module for AIAlchemy
Creates tables and populates with sample data with better error handling
"""

import asyncio
import sys
import traceback
from datetime import datetime

async def create_tables():
    """Create all database tables"""
    try:
        print("🔧 Creating database tables...")
        from app.database import Base, engine
        
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        print("✅ Database tables created successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to create database tables: {e}")
        traceback.print_exc()
        return False

async def add_sample_data():
    """Add sample data to prevent empty table errors"""
    try:
        print("📊 Adding sample startup data...")
        from app.database import async_session_local
        from app.models import StartupApplication, ApplicationStatus, FundingStage
        from sqlalchemy import select
        
        async with async_session_local() as session:
            # Check if data already exists
            result = await session.execute(select(StartupApplication))
            existing = result.fetchall()
            
            if len(existing) == 0:
                print("➕ Adding sample startup applications...")
                
                sample_apps = [
                    StartupApplication(
                        company_name="TechCorp AI",
                        founders_name="John Doe",
                        email="john@techcorp.ai",
                        status=ApplicationStatus.NEW,
                        funding_stage=FundingStage.SEED,
                        funding_amount=1000000.0,
                        industry="AI/ML",
                        description="AI-powered analytics platform",
                        application_date=datetime.utcnow()
                    ),
                    StartupApplication(
                        company_name="GreenTech Solutions",
                        founders_name="Jane Smith",
                        email="jane@greentech.com",
                        status=ApplicationStatus.AI_ANALYSIS,
                        funding_stage=FundingStage.SERIES_A,
                        funding_amount=5000000.0,
                        industry="CleanTech",
                        description="Renewable energy management system",
                        application_date=datetime.utcnow()
                    ),
                    StartupApplication(
                        company_name="HealthAI Inc",
                        founders_name="Dr. Mike Johnson",
                        email="mike@healthai.com",
                        status=ApplicationStatus.COMPLETED,
                        funding_stage=FundingStage.SEED,
                        funding_amount=2000000.0,
                        industry="HealthTech",
                        description="AI-powered medical diagnosis platform",
                        application_date=datetime.utcnow()
                    )
                ]
                
                for app in sample_apps:
                    session.add(app)
                
                await session.commit()
                print(f"✅ Added {len(sample_apps)} sample startup applications")
            else:
                print(f"ℹ️ Database already has {len(existing)} startup applications")
                
        return True
                
    except Exception as e:
        print(f"❌ Failed to add sample data: {e}")
        traceback.print_exc()
        return False

async def verify_tables():
    """Verify that tables exist and have data"""
    try:
        print("🔍 Verifying database tables...")
        from app.database import async_session_local
        from sqlalchemy import text
        
        async with async_session_local() as session:
            # Check if startup_applications table exists and has data
            result = await session.execute(
                text("SELECT COUNT(*) FROM startup_applications")
            )
            count = result.scalar()
            print(f"📊 Found {count} startup applications in database")
            return count > 0
            
    except Exception as e:
        print(f"❌ Failed to verify tables: {e}")
        return False

async def init_database():
    """Initialize database with tables and sample data"""
    try:
        print("🚀 Starting database initialization...")
        
        # Step 1: Create tables
        tables_created = await create_tables()
        if not tables_created:
            print("⚠️ Table creation failed, but continuing...")
        
        # Step 2: Add sample data
        data_added = await add_sample_data()
        if not data_added:
            print("⚠️ Sample data addition failed, but continuing...")
        
        # Step 3: Verify everything works
        verified = await verify_tables()
        
        if verified:
            print("✅ Database initialization completed successfully!")
            return True
        else:
            print("⚠️ Database initialization completed with warnings")
            return False
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        traceback.print_exc()
        return False

# For direct execution
if __name__ == "__main__":
    asyncio.run(init_database())