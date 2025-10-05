"""
Authentication endpoint tests - Login, Registration, JWT handling
"""

import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_login_valid_credentials(client: AsyncClient):
    """Test login with valid credentials."""
    login_data = {
        "email": "test@example.com",
        "password": "TempPass123!"
    }
    
    response = await client.post("/api/auth/login", json=login_data)
    
    assert response.status_code == 200
    data = response.json()
    
    # Check response structure
    assert "access_token" in data
    assert "refresh_token" in data
    assert "token_type" in data
    assert "expires_in" in data
    assert "user" in data
    
    # Check token type
    assert data["token_type"] == "bearer"
    
    # Check user data
    user = data["user"]
    assert user["email"] == "test@example.com"
    assert user["full_name"] == "Test User"
    assert user["role"] == "admin"

@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient):
    """Test login with invalid credentials."""
    login_data = {
        "email": "test@example.com",
        "password": "wrongpassword"
    }
    
    response = await client.post("/api/auth/login", json=login_data)
    
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data

@pytest.mark.asyncio
async def test_login_nonexistent_user(client: AsyncClient):
    """Test login with non-existent user."""
    login_data = {
        "email": "nonexistent@example.com",
        "password": "TempPass123!"
    }
    
    response = await client.post("/api/auth/login", json=login_data)
    
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_registration_valid_data(client: AsyncClient):
    """Test user registration with valid data."""
    registration_data = {
        "email": "newuser@example.com",
        "password": "NewPass123!",
        "full_name": "New User",
        "title": "Software Engineer"
    }
    
    response = await client.post("/api/auth/register", json=registration_data)
    
    assert response.status_code == 201
    data = response.json()
    
    assert "message" in data
    assert "user" in data
    assert data["user"]["email"] == "newuser@example.com"
    assert data["user"]["full_name"] == "New User"
    assert data["user"]["role"] == "viewer"  # Default role

@pytest.mark.asyncio
async def test_registration_existing_email(client: AsyncClient):
    """Test registration with already existing email."""
    registration_data = {
        "email": "test@example.com",  # Already exists in test data
        "password": "NewPass123!",
        "full_name": "Duplicate User"
    }
    
    response = await client.post("/api/auth/register", json=registration_data)
    
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data

@pytest.mark.asyncio
async def test_registration_weak_password(client: AsyncClient):
    """Test registration with weak password."""
    registration_data = {
        "email": "weakpass@example.com",
        "password": "123",  # Too weak
        "full_name": "Weak Password User"
    }
    
    response = await client.post("/api/auth/register", json=registration_data)
    
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data

@pytest.mark.asyncio
async def test_get_current_user_profile(authenticated_client: AsyncClient):
    """Test getting current user profile with valid token."""
    response = await authenticated_client.get("/api/auth/me")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["email"] == "test@example.com"
    assert data["full_name"] == "Test User"
    assert data["role"] == "admin"

@pytest.mark.asyncio
async def test_get_current_user_without_token(client: AsyncClient):
    """Test accessing protected endpoint without token."""
    response = await client.get("/api/auth/me")
    
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_token_refresh(client: AsyncClient):
    """Test JWT token refresh functionality."""
    # First login to get tokens
    login_data = {
        "email": "test@example.com",
        "password": "TempPass123!"
    }
    
    login_response = await client.post("/api/auth/login", json=login_data)
    assert login_response.status_code == 200
    
    login_data = login_response.json()
    refresh_token = login_data["refresh_token"]
    
    # Test token refresh
    refresh_data = {"refresh_token": refresh_token}
    response = await client.post("/api/auth/refresh", json=refresh_data)
    
    assert response.status_code == 200
    data = response.json()
    
    assert "access_token" in data
    assert "token_type" in data
    assert "expires_in" in data

@pytest.mark.asyncio
async def test_logout(authenticated_client: AsyncClient):
    """Test user logout."""
    response = await authenticated_client.post("/api/auth/logout")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "message" in data

@pytest.mark.asyncio
async def test_password_validation_edge_cases(client: AsyncClient):
    """Test various password validation scenarios."""
    
    test_cases = [
        {
            "password": "short",
            "should_fail": True,
            "description": "too short"
        },
        {
            "password": "alllowercase123!",
            "should_fail": True, 
            "description": "missing uppercase"
        },
        {
            "password": "ALLUPPERCASE123!",
            "should_fail": True,
            "description": "missing lowercase"  
        },
        {
            "password": "NoNumbers!",
            "should_fail": True,
            "description": "missing numbers"
        },
        {
            "password": "NoSpecialChars123",
            "should_fail": True,
            "description": "missing special characters"
        },
        {
            "password": "ValidPassword123!",
            "should_fail": False,
            "description": "valid password"
        }
    ]
    
    for case in test_cases:
        registration_data = {
            "email": f"test_{case['description'].replace(' ', '_')}@example.com",
            "password": case["password"],
            "full_name": f"Test User {case['description']}"
        }
        
        response = await client.post("/api/auth/register", json=registration_data)
        
        if case["should_fail"]:
            assert response.status_code == 400, f"Password '{case['password']}' should have failed ({case['description']})"
        else:
            assert response.status_code == 201, f"Password '{case['password']}' should have succeeded ({case['description']})"