"""
Pytest configuration and fixtures for AIAlchemy backend testing
"""

import pytest
import asyncio
from httpx import AsyncClient
from fastapi.testclient import TestClient
import tempfile
import os
from pathlib import Path

# Import the FastAPI app
import sys
sys.path.append(str(Path(__file__).parent.parent))

from app.main import app
from app.core.database import database_manager
from app.models import Base, User, StartupApplication, Industry, UserRole
from app.auth.simple_password import simple_hash_password

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
async def test_app():
    """Create a test FastAPI application with isolated database."""
    
    # Create temporary database file
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db.close()
    
    # Set test database URL
    test_db_url = f"sqlite+aiosqlite:///{temp_db.name}"
    
    # Override the database URL for testing
    import app.core.config
    original_get_settings = app.core.config.get_settings
    
    class TestSettings:
        def __init__(self):
            self.database_url = test_db_url
            self.is_development = True
            self.database_pool_size = 1
            self.database_max_overflow = 0
            self.secret_key = "test-secret-key"
            self.jwt_secret_key = "test-jwt-secret"
            self.jwt_algorithm = "HS256"
            self.jwt_expiration_hours = 24
    
    app.core.config.get_settings = lambda: TestSettings()
    
    try:
        # Initialize test database
        await database_manager.connect()
        
        # Create tables
        async with database_manager.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        # Add test data
        await _create_test_data()
        
        yield app
        
    finally:
        # Cleanup
        await database_manager.disconnect()
        os.unlink(temp_db.name)
        app.core.config.get_settings = original_get_settings

async def _create_test_data():
    """Create test data for testing."""
    async with database_manager.get_session() as session:
        # Create test industries
        ai_industry = Industry(name="AI/ML", description="Artificial Intelligence")
        fintech_industry = Industry(name="FinTech", description="Financial Technology")
        
        session.add(ai_industry)
        session.add(fintech_industry)
        await session.commit()
        await session.refresh(ai_industry)
        await session.refresh(fintech_industry)
        
        # Create test users
        test_users = [
            User(
                email="test@example.com",
                hashed_password=simple_hash_password("TempPass123!"),
                full_name="Test User",
                title="Developer",
                role=UserRole.ADMIN,
                is_active=True
            ),
            User(
                email="analyst@example.com", 
                hashed_password=simple_hash_password("AnalystPass123!"),
                full_name="Test Analyst",
                title="AI Analyst",
                role=UserRole.ANALYST,
                is_active=True
            )
        ]
        
        for user in test_users:
            session.add(user)
        
        await session.commit()
        
        # Create test startup applications
        test_startups = [
            StartupApplication(
                company_name="TestCorp AI",
                contact_name="John Doe",
                contact_email="john@testcorp.ai",
                website="https://testcorp.ai",
                industry_id=ai_industry.id,
                funding_amount_requested=1000000.0,
                current_arr=100000.0,
                runway_months=18
            ),
            StartupApplication(
                company_name="FinTech Solutions",
                contact_name="Jane Smith", 
                contact_email="jane@fintech.com",
                website="https://fintech.com",
                industry_id=fintech_industry.id,
                funding_amount_requested=2000000.0,
                current_arr=500000.0,
                runway_months=24
            )
        ]
        
        for startup in test_startups:
            session.add(startup)
            
        await session.commit()

@pytest.fixture
async def client(test_app):
    """Create async HTTP client for testing."""
    async with AsyncClient(app=test_app, base_url="http://test") as ac:
        yield ac

@pytest.fixture
def sync_client(test_app):
    """Create synchronous test client for simple tests."""
    return TestClient(test_app)

@pytest.fixture
async def authenticated_client(client):
    """Create authenticated HTTP client with valid JWT token."""
    
    # Login to get token
    login_data = {
        "email": "test@example.com",
        "password": "TempPass123!"
    }
    
    response = await client.post("/api/auth/login", json=login_data)
    assert response.status_code == 200
    
    token_data = response.json()
    access_token = token_data["access_token"]
    
    # Create new client with authorization header
    headers = {"Authorization": f"Bearer {access_token}"}
    
    async with AsyncClient(app=client.app, base_url="http://test", headers=headers) as auth_client:
        yield auth_client

@pytest.fixture
async def analyst_client(client):
    """Create authenticated HTTP client with analyst role."""
    
    login_data = {
        "email": "analyst@example.com", 
        "password": "AnalystPass123!"
    }
    
    response = await client.post("/api/auth/login", json=login_data)
    assert response.status_code == 200
    
    token_data = response.json()
    access_token = token_data["access_token"]
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    async with AsyncClient(app=client.app, base_url="http://test", headers=headers) as auth_client:
        yield auth_client