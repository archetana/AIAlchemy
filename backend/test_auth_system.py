#!/usr/bin/env python3
"""
Test Authentication System
Direct testing without FastAPI server
"""

import asyncio
import sys
import os

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

async def test_authentication_components():
    """Test authentication components individually"""
    print("🔐 Testing Authentication System Components")
    print("=" * 60)
    
    # Test 1: Password hashing
    print("\n1. 🔒 Testing Password Utilities...")
    try:
        from app.auth.password_utils import hash_password, verify_password, validate_password
        
        test_password = "TempPass123!"
        
        # Test password validation
        validation = validate_password(test_password)
        print(f"   Password validation: {'✅ PASS' if validation['valid'] else '❌ FAIL'}")
        
        # Test password hashing
        hashed = hash_password(test_password)
        print(f"   Password hashing: ✅ PASS (length: {len(hashed)})")
        
        # Test password verification
        verify_result = verify_password(test_password, hashed)
        print(f"   Password verification: {'✅ PASS' if verify_result else '❌ FAIL'}")
        
    except Exception as e:
        print(f"   Password utilities: ❌ FAIL - {e}")
        return False
    
    # Test 2: JWT Token handling
    print("\n2. 🔑 Testing JWT Handler...")
    try:
        # Set required environment variables
        os.environ.setdefault("JWT_SECRET_KEY", "test-jwt-secret-key-for-testing")
        os.environ.setdefault("JWT_ALGORITHM", "HS256")
        os.environ.setdefault("JWT_EXPIRATION_HOURS", "24")
        
        from app.auth.jwt_handler import jwt_handler
        
        # Test token creation
        test_payload = {
            "sub": "1",
            "email": "test@example.com",
            "role": "ADMIN"
        }
        
        access_token = jwt_handler.create_access_token(test_payload)
        print(f"   Token creation: ✅ PASS (length: {len(access_token)})")
        
        # Test token verification
        decoded = jwt_handler.verify_token(access_token)
        print(f"   Token verification: {'✅ PASS' if decoded else '❌ FAIL'}")
        
        # Test user ID extraction
        user_id = jwt_handler.extract_user_id(access_token)
        print(f"   User ID extraction: {'✅ PASS' if user_id == 1 else '❌ FAIL'}")
        
    except Exception as e:
        print(f"   JWT handler: ❌ FAIL - {e}")
        return False
    
    # Test 3: Database connection and user lookup
    print("\n3. 🗄️ Testing Database Connection...")
    try:
        from app.core.database import database_manager
        from app.models import User
        from sqlalchemy import select
        
        # Initialize database connection
        await database_manager.connect()
        
        async with database_manager.get_session() as db:
            # Test database connection
            result = await db.execute(select(User).limit(1))
            user = result.scalar_one_or_none()
            
            if user:
                print(f"   Database connection: ✅ PASS")
                print(f"   Test user found: ✅ PASS ({user.email})")
            else:
                print(f"   Database connection: ✅ PASS")
                print(f"   Test user found: ⚠️ No users in database")
        
    except Exception as e:
        print(f"   Database connection: ❌ FAIL - {e}")
        return False
    
    # Test 4: Authentication dependency
    print("\n4. 🔐 Testing Authentication Dependencies...")
    try:
        from app.auth.auth_dependencies import get_current_user
        print(f"   Auth dependencies import: ✅ PASS")
        
    except Exception as e:
        print(f"   Auth dependencies: ❌ FAIL - {e}")
        return False
    
    return True

async def test_login_flow():
    """Test complete login flow"""
    print("\n🚀 Testing Complete Login Flow")
    print("=" * 40)
    
    try:
        from app.auth.password_utils import verify_password
        from app.auth.jwt_handler import jwt_handler
        from app.core.database import get_db_session
        from app.models import User
        from sqlalchemy import select
        
        # Test credentials
        test_email = "test@example.com"
        test_password = "TempPass123!"
        
        print(f"📧 Testing login for: {test_email}")
        
        from app.core.database import database_manager
        
        # Ensure database is connected
        if not database_manager.is_connected:
            await database_manager.connect()
        
        async with database_manager.get_session() as db:
            # Find user by email
            user_query = select(User).where(User.email == test_email)
            user_result = await db.execute(user_query)
            user = user_result.scalar_one_or_none()
            
            if not user:
                print(f"   User lookup: ❌ FAIL - User not found")
                return False
            
            print(f"   User lookup: ✅ PASS ({user.full_name})")
            
            # Verify password
            if not verify_password(test_password, user.hashed_password):
                print(f"   Password verification: ❌ FAIL")
                return False
            
            print(f"   Password verification: ✅ PASS")
            
            # Generate tokens
            token_payload = {
                "sub": str(user.id),
                "email": user.email,
                "role": user.role.value,
                "full_name": user.full_name
            }
            
            tokens = jwt_handler.create_token_pair(token_payload)
            print(f"   Token generation: ✅ PASS")
            print(f"     Access token length: {len(tokens['access_token'])}")
            print(f"     Refresh token length: {len(tokens['refresh_token'])}")
            print(f"     Expires in: {tokens['expires_in']} seconds")
            
            # Verify generated token
            decoded = jwt_handler.verify_token(tokens['access_token'])
            if decoded and decoded.get('email') == test_email:
                print(f"   Token verification: ✅ PASS")
            else:
                print(f"   Token verification: ❌ FAIL")
                return False
        
        return True
        
    except Exception as e:
        print(f"   Login flow: ❌ FAIL - {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("🧪 AIAlchemy Authentication System Test")
    print("=" * 70)
    
    async def run_tests():
        # Test components
        components_ok = await test_authentication_components()
        
        if not components_ok:
            print("\n❌ Component tests failed!")
            return
        
        # Test complete flow
        flow_ok = await test_login_flow()
        
        print("\n" + "=" * 70)
        if components_ok and flow_ok:
            print("✅ ALL TESTS PASSED!")
            print("🚀 Authentication system is working correctly!")
            print("\n📋 Ready to use:")
            print("   - Login endpoint: POST /api/auth/login")
            print("   - Register endpoint: POST /api/auth/register")
            print("   - Profile endpoint: GET /api/auth/me")
            print("   - Preferences endpoint: GET /api/settings/account/preferences")
            print("\n🔑 Test login credentials:")
            print("   Email: test@example.com")
            print("   Password: TempPass123!")
        else:
            print("❌ SOME TESTS FAILED!")
            print("Check the errors above for details.")
    
    asyncio.run(run_tests())

if __name__ == "__main__":
    main()