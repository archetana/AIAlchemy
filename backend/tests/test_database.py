"""
Database connectivity and operations tests
"""

import pytest
from httpx import AsyncClient
from app.core.database import database_manager
from app.models import StartupApplication, Industry, User
from sqlalchemy import select

@pytest.mark.asyncio
async def test_database_connection():
    """Test basic database connectivity."""
    assert database_manager.is_connected
    
    # Test basic query
    async with database_manager.get_session() as session:
        result = await session.execute(select(User))
        users = result.fetchall()
        assert len(users) >= 2  # Should have test users

@pytest.mark.asyncio
async def test_startup_applications_exist():
    """Test that sample startup applications were created."""
    async with database_manager.get_session() as session:
        result = await session.execute(select(StartupApplication))
        startups = result.fetchall()
        assert len(startups) >= 2

@pytest.mark.asyncio
async def test_industries_exist():
    """Test that sample industries were created."""
    async with database_manager.get_session() as session:
        result = await session.execute(select(Industry))
        industries = result.fetchall()
        assert len(industries) >= 2

@pytest.mark.asyncio 
async def test_user_relationships():
    """Test database relationships work correctly."""
    async with database_manager.get_session() as session:
        # Get user
        result = await session.execute(
            select(User).where(User.email == "test@example.com")
        )
        user = result.scalar_one()
        
        assert user is not None
        assert user.email == "test@example.com"
        assert user.full_name == "Test User"

@pytest.mark.asyncio
async def test_startup_industry_relationship():
    """Test startup-industry foreign key relationship."""
    async with database_manager.get_session() as session:
        # Get startup with industry
        result = await session.execute(
            select(StartupApplication).where(
                StartupApplication.company_name == "TestCorp AI"
            )
        )
        startup = result.scalar_one()
        
        assert startup is not None
        assert startup.industry_id is not None
        
        # Verify industry exists
        industry_result = await session.execute(
            select(Industry).where(Industry.id == startup.industry_id)
        )
        industry = industry_result.scalar_one()
        assert industry is not None
        assert industry.name in ["AI/ML", "FinTech"]