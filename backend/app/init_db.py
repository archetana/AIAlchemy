"""
Database initialization module for AIAlchemy
Creates tables and populates with sample data
"""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from app.database import Base, engine, DATABASE_URL
from app.models import *  # Import all models to register them
import structlog

logger = structlog.get_logger()

async def create_tables():
    """Create all database tables"""
    try:
        logger.info("Creating database tables...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("✅ Database tables created successfully")
        return True
    except Exception as e:
        logger.error("❌ Failed to create database tables", error=str(e))
        return False

async def add_sample_data():
    """Add sample data to prevent empty table errors"""
    from app.database import async_session_local
    from app.models import StartupApplication, ApplicationStatus, FundingStage
    from datetime import datetime
    
    try:
        async with async_session_local() as session:
            # Check if data already exists
            from sqlalchemy import select
            result = await session.execute(select(StartupApplication))
            existing = result.fetchall()
            
            if len(existing) == 0:
                logger.info("Adding sample startup applications...")
                
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
                logger.info(f"✅ Added {len(sample_apps)} sample startup applications")
            else:
                logger.info(f"ℹ️ Database already has {len(existing)} startup applications")
                
    except Exception as e:
        logger.error("❌ Failed to add sample data", error=str(e))

async def init_database():
    """Initialize database with tables and sample data"""
    try:
        # Create tables
        success = await create_tables()
        if not success:
            return False
        
        # Add sample data
        await add_sample_data()
            
        logger.info("✅ Database initialization completed")
        return True
        
    except Exception as e:
        logger.error("❌ Database initialization failed", error=str(e))
        return False

# For direct execution
if __name__ == "__main__":
    asyncio.run(init_database())