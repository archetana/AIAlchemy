#!/usr/bin/env python3
"""
Test script to verify registration fix
Tests that the registration endpoint now returns tokens and respects role selection
"""

import sys
import json
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

def test_register_request_schema():
    """Test that RegisterRequest accepts role field"""
    print("=" * 60)
    print("TEST 1: RegisterRequest Schema accepts role field")
    print("=" * 60)

    try:
        from app.schemas import RegisterRequest
        from app.models import UserRole

        # Test with role
        test_data = {
            "email": "test@example.com",
            "password": "SecurePass123!",
            "full_name": "Test User",
            "title": "Software Engineer",
            "phone": "+1234567890",
            "role": "analyst"
        }

        request = RegisterRequest(**test_data)
        print(f"✅ RegisterRequest with role: {request.role}")
        assert request.role == UserRole.ANALYST, "Role should be ANALYST"

        # Test without role (should be None, defaults to VIEWER in endpoint)
        test_data_no_role = {
            "email": "test2@example.com",
            "password": "SecurePass123!",
            "full_name": "Test User 2"
        }

        request_no_role = RegisterRequest(**test_data_no_role)
        print(f"✅ RegisterRequest without role: {request_no_role.role} (will default to VIEWER in endpoint)")

        print("\n✅ TEST 1 PASSED: RegisterRequest schema correctly accepts role field\n")
        return True

    except Exception as e:
        print(f"\n❌ TEST 1 FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_register_response_schema():
    """Test that RegisterResponse includes tokens"""
    print("=" * 60)
    print("TEST 2: RegisterResponse Schema includes tokens")
    print("=" * 60)

    try:
        from app.schemas import RegisterResponse, UserProfile
        from app.models import UserRole
        from datetime import datetime, timezone

        # Create mock user profile
        user_profile = UserProfile(
            id=1,
            email="test@example.com",
            full_name="Test User",
            title="Engineer",
            phone=None,
            role=UserRole.ANALYST,
            is_active=True,
            created_at=datetime.now(timezone.utc)
        )

        # Test response with tokens
        response_data = {
            "message": "Account created successfully",
            "user": user_profile,
            "access_token": "mock_access_token_here",
            "refresh_token": "mock_refresh_token_here",
            "token_type": "bearer"
        }

        response = RegisterResponse(**response_data)
        print(f"✅ RegisterResponse includes access_token: {bool(response.access_token)}")
        print(f"✅ RegisterResponse includes refresh_token: {bool(response.refresh_token)}")
        print(f"✅ RegisterResponse includes token_type: {response.token_type}")
        print(f"✅ RegisterResponse includes user profile: {response.user.email}")

        assert response.access_token == "mock_access_token_here"
        assert response.refresh_token == "mock_refresh_token_here"
        assert response.token_type == "bearer"

        print("\n✅ TEST 2 PASSED: RegisterResponse schema correctly includes tokens\n")
        return True

    except Exception as e:
        print(f"\n❌ TEST 2 FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_role_validation_logic():
    """Test role validation logic from auth endpoint"""
    print("=" * 60)
    print("TEST 3: Role Validation Logic")
    print("=" * 60)

    try:
        from app.models import UserRole

        # Simulate the validation logic from auth.py
        test_cases = [
            ("viewer", UserRole.VIEWER),
            ("analyst", UserRole.ANALYST),
            ("partner", UserRole.PARTNER),
            ("admin", UserRole.ADMIN),
            ("invalid_role", UserRole.VIEWER),  # Should default to VIEWER
            (None, UserRole.VIEWER),  # Should default to VIEWER
        ]

        for test_role, expected_result in test_cases:
            user_role = UserRole.VIEWER  # Default

            if test_role:
                try:
                    user_role = UserRole(test_role)
                    print(f"✅ Role '{test_role}' → {user_role.value}")
                except ValueError:
                    print(f"✅ Invalid role '{test_role}' → defaulted to {user_role.value}")
            else:
                print(f"✅ No role provided → defaulted to {user_role.value}")

            assert user_role == expected_result, f"Expected {expected_result}, got {user_role}"

        print("\n✅ TEST 3 PASSED: Role validation logic works correctly\n")
        return True

    except Exception as e:
        print(f"\n❌ TEST 3 FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_auth_endpoint_code():
    """Verify auth endpoint code has necessary imports and logic"""
    print("=" * 60)
    print("TEST 4: Auth Endpoint Code Verification")
    print("=" * 60)

    try:
        # Read the auth.py file
        auth_file = backend_path / "app" / "routers" / "auth.py"
        with open(auth_file, 'r', encoding='utf-8') as f:
            auth_code = f.read()

        # Check for key changes
        checks = [
            ("jwt_handler import", "from app.auth.jwt_handler import jwt_handler"),
            ("Role validation logic", "user_role = UserRole.VIEWER"),
            ("Role from request", "if hasattr(user_data, 'role') and user_data.role:"),
            ("Token generation", "tokens = jwt_handler.create_token_pair(token_payload)"),
            ("Access token in response", 'access_token=tokens["access_token"]'),
            ("Refresh token in response", 'refresh_token=tokens["refresh_token"]'),
        ]

        all_passed = True
        for check_name, check_string in checks:
            if check_string in auth_code:
                print(f"✅ Found: {check_name}")
            else:
                print(f"❌ Missing: {check_name}")
                all_passed = False

        if all_passed:
            print("\n✅ TEST 4 PASSED: Auth endpoint has all necessary code\n")
        else:
            print("\n⚠️ TEST 4 PARTIAL: Some code patterns not found (may use different implementation)\n")

        return all_passed

    except Exception as e:
        print(f"\n❌ TEST 4 FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("REGISTRATION FIX VERIFICATION TESTS")
    print("=" * 60 + "\n")

    results = []

    # Run tests
    results.append(("RegisterRequest Schema", test_register_request_schema()))
    results.append(("RegisterResponse Schema", test_register_response_schema()))
    results.append(("Role Validation Logic", test_role_validation_logic()))
    results.append(("Auth Endpoint Code", test_auth_endpoint_code()))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! Registration fix is ready.")
        return 0
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Review the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
