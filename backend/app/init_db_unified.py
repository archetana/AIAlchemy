"""
Unified database initialization module for AIAlchemy
Creates tables and populates with sample data - works with both startup.sh and main.py lifespan
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
        from app.models import StartupApplication, ApplicationStatus, FundingStage, Industry, User, UserRole
        from app.auth.password_utils import hash_password
        from sqlalchemy import select
        
        async with async_session_local() as session:
            # Check if data already exists
            result = await session.execute(select(StartupApplication))
            existing = result.fetchall()
            
            if len(existing) == 0:
                print("➕ Adding sample industries...")
                
                # First, create sample industries
                sample_industries = [
                    Industry(name="AI/ML", description="Artificial Intelligence and Machine Learning"),
                    Industry(name="CleanTech", description="Clean Technology and Renewable Energy"),
                    Industry(name="HealthTech", description="Healthcare Technology and Medical Devices"),
                    Industry(name="FinTech", description="Financial Technology"),
                    Industry(name="EdTech", description="Educational Technology")
                ]
                
                for industry in sample_industries:
                    session.add(industry)
                
                await session.commit()
                
                # Get the created industries
                ai_industry = await session.execute(select(Industry).where(Industry.name == "AI/ML"))
                ai_industry = ai_industry.scalar_one()
                
                cleantech_industry = await session.execute(select(Industry).where(Industry.name == "CleanTech"))
                cleantech_industry = cleantech_industry.scalar_one()
                
                healthtech_industry = await session.execute(select(Industry).where(Industry.name == "HealthTech"))
                healthtech_industry = healthtech_industry.scalar_one()
                
                print("➕ Adding sample startup applications...")
                
                sample_apps = [
                    StartupApplication(
                        company_name="TechCorp AI",
                        contact_name="John Doe",
                        contact_email="john@techcorp.ai",
                        website="https://techcorp.ai",
                        status=ApplicationStatus.NEW,
                        funding_stage=FundingStage.SEED,
                        funding_amount_requested=1000000.0,
                        current_arr=100000.0,
                        runway_months=18,
                        industry_id=ai_industry.id
                    ),
                    StartupApplication(
                        company_name="GreenTech Solutions",
                        contact_name="Jane Smith",
                        contact_email="jane@greentech.com",
                        website="https://greentech.com",
                        status=ApplicationStatus.AI_ANALYSIS,
                        funding_stage=FundingStage.SERIES_A,
                        funding_amount_requested=5000000.0,
                        current_arr=2000000.0,
                        runway_months=24,
                        industry_id=cleantech_industry.id
                    ),
                    StartupApplication(
                        company_name="HealthAI Inc",
                        contact_name="Dr. Mike Johnson",
                        contact_email="mike@healthai.com",
                        website="https://healthai.com",
                        status=ApplicationStatus.COMPLETED,
                        funding_stage=FundingStage.SEED,
                        funding_amount_requested=2000000.0,
                        current_arr=500000.0,
                        runway_months=20,
                        industry_id=healthtech_industry.id
                    )
                ]
                
                for app in sample_apps:
                    session.add(app)
                
                await session.commit()
                print(f"✅ Added {len(sample_industries)} industries and {len(sample_apps)} startup applications")
                
                # Add sample users for testing
                print("👤 Adding sample users...")
                
                sample_users = [
                    User(
                        email="test@example.com",
                        hashed_password=hash_password("TempPass123!"),
                        full_name="Test User",
                        title="Developer", 
                        role=UserRole.ADMIN,
                        is_active=True
                    ),
                    User(
                        email="admin@aialchemy.com",
                        hashed_password=hash_password("AdminPass123!"),
                        full_name="Admin User",
                        title="Administrator",
                        role=UserRole.ADMIN,
                        is_active=True
                    ),
                    User(
                        email="analyst@aialchemy.com", 
                        hashed_password=hash_password("AnalystPass123!"),
                        full_name="AI Analyst",
                        title="Senior AI Analyst",
                        role=UserRole.ANALYST,
                        is_active=True
                    )
                ]
                
                for user in sample_users:
                    session.add(user)
                    
                await session.commit()
                print(f"✅ Added {len(sample_users)} sample users")
                
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
        traceback.print_exc()
        return False

async def initialize_file_storage():
    """Initialize file storage directories"""
    try:
        print("📁 Initializing file storage...")
        import os
        from pathlib import Path
        
        # Create local upload directories
        upload_base = Path(os.getenv('LOCAL_UPLOAD_PATH', './uploads'))
        upload_base.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories for different file types
        for file_type in ['pitch_deck', 'financial_docs', 'team_info', 'legal_docs', 'media']:
            (upload_base / file_type).mkdir(exist_ok=True)
        
        print(f"✅ File storage initialized at: {upload_base.absolute()}")
        return True
        
    except Exception as e:
        print(f"⚠️ File storage initialization failed: {e}")
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
        
        # Step 3: Initialize file upload directories
        await initialize_file_storage()
        
        # Step 4: Verify everything works
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