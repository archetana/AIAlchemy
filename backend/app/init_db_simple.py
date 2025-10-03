"""
Simple database initialization for AIAlchemy
"""

import asyncio
from datetime import datetime

async def init_database_simple():
    """Simple database initialization with better error handling"""
    try:
        print("🚀 Initializing database...")
        
        # Import here to avoid circular imports
        from app.database import Base, engine, async_session_local
        from app.models import StartupApplication, ApplicationStatus, FundingStage
        from sqlalchemy import select
        
        # Create tables
        print("📋 Creating tables...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Tables created")
        
        # Add sample data
        print("📊 Adding sample data...")
        async with async_session_local() as session:
            # Check existing data
            result = await session.execute(select(StartupApplication))
            existing = result.fetchall()
            
            if len(existing) == 0:
                # Add sample applications
                apps = [
                    StartupApplication(
                        company_name="TechCorp AI", founders_name="John Doe",
                        email="john@techcorp.ai", status=ApplicationStatus.NEW,
                        funding_stage=FundingStage.SEED, funding_amount=1000000.0,
                        industry="AI/ML", description="AI analytics platform",
                        application_date=datetime.utcnow()
                    ),
                    StartupApplication(
                        company_name="GreenTech Solutions", founders_name="Jane Smith", 
                        email="jane@greentech.com", status=ApplicationStatus.AI_ANALYSIS,
                        funding_stage=FundingStage.SERIES_A, funding_amount=5000000.0,
                        industry="CleanTech", description="Renewable energy system",
                        application_date=datetime.utcnow()
                    )
                ]
                
                for app in apps:
                    session.add(app)
                await session.commit()
                print(f"✅ Added {len(apps)} sample applications")
            else:
                print(f"ℹ️ Found {len(existing)} existing applications")
        
        return True
        
    except Exception as e:
        print(f"❌ Database init error: {e}")
        import traceback
        traceback.print_exc()
        return False