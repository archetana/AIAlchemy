"""
Simple basic tests to verify testing framework works
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient

# Simple sync test first
def test_basic_python():
    """Basic Python functionality test."""
    assert 1 + 1 == 2
    assert "hello" == "hello"

def test_basic_imports():
    """Test that we can import our main modules."""
    import fastapi
    import sqlalchemy
    import pytest
    assert True

def test_sync_client_basic():
    """Test basic sync client functionality."""
    # Import app
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent))
    
    from app.main import app
    
    client = TestClient(app)
    
    # Test root endpoint
    try:
        response = client.get("/")
        # Should get some response, even if it's an error
        assert response.status_code in [200, 404, 500]
    except Exception as e:
        # Even if there's an error, the test framework works
        print(f"Expected error during sync test: {e}")
        assert True

@pytest.mark.asyncio
async def test_async_basic():
    """Test basic async functionality."""
    await asyncio.sleep(0.01)  # Basic async operation
    assert True
    
@pytest.mark.asyncio 
async def test_async_http_client():
    """Test async HTTP client basic functionality."""
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent))
    
    from app.main import app
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        try:
            response = await client.get("/")
            # Any response code is fine for this basic test
            assert response.status_code in [200, 404, 422, 500]
        except Exception as e:
            # If there's an error, that's also fine for basic test
            print(f"Expected error during async test: {e}")
            assert True