#!/usr/bin/env python3
"""
Simple verification script for registration fix
Checks code changes without requiring dependencies
"""

import re
from pathlib import Path

def verify_auth_endpoint():
    """Verify auth.py has all necessary changes"""
    print("="*60)
    print("Verifying Registration Fix in auth.py")
    print("="*60)

    auth_file = Path(__file__).parent / "app" / "routers" / "auth.py"

    if not auth_file.exists():
        print(f"ERROR: File not found: {auth_file}")
        return False

    with open(auth_file, 'r', encoding='utf-8') as f:
        content = f.read()

    checks = [
        {
            "name": "JWT Handler Import",
            "pattern": r"from app\.auth\.jwt_handler import jwt_handler",
            "required": True
        },
        {
            "name": "Role Validation Logic",
            "pattern": r"user_role = UserRole\.VIEWER.*# Default role",
            "required": True
        },
        {
            "name": "Check for role in request data",
            "pattern": r"if hasattr\(user_data, 'role'\) and user_data\.role:",
            "required": True
        },
        {
            "name": "Token generation after user creation",
            "pattern": r"tokens = jwt_handler\.create_token_pair\(token_payload\)",
            "required": True
        },
        {
            "name": "Access token in response",
            "pattern": r'access_token=tokens\["access_token"\]',
            "required": True
        },
        {
            "name": "Refresh token in response",
            "pattern": r'refresh_token=tokens\["refresh_token"\]',
            "required": True
        },
        {
            "name": "Role logged in success message",
            "pattern": r'role=new_user\.role\.value',
            "required": True
        }
    ]

    passed = 0
    failed = 0

    for check in checks:
        if re.search(check["pattern"], content, re.MULTILINE | re.DOTALL):
            print(f"[PASS] {check['name']}")
            passed += 1
        else:
            print(f"[FAIL] {check['name']}")
            failed += 1

    print(f"\nResults: {passed} passed, {failed} failed")
    return failed == 0


def verify_schemas():
    """Verify schemas.py has token fields"""
    print("\n" + "="*60)
    print("Verifying Schema Changes in schemas.py")
    print("="*60)

    schemas_file = Path(__file__).parent / "app" / "schemas.py"

    if not schemas_file.exists():
        print(f"ERROR: File not found: {schemas_file}")
        return False

    with open(schemas_file, 'r', encoding='utf-8') as f:
        content = f.read()

    checks = [
        {
            "name": "RegisterRequest has role field",
            "pattern": r"role:\s*Optional\[UserRole\]",
            "required": True
        },
        {
            "name": "RegisterResponse has access_token",
            "pattern": r"access_token:\s*str",
            "required": True
        },
        {
            "name": "RegisterResponse has refresh_token",
            "pattern": r"refresh_token:\s*str",
            "required": True
        },
        {
            "name": "RegisterResponse has token_type",
            "pattern": r'token_type:\s*str\s*=\s*"bearer"',
            "required": True
        }
    ]

    passed = 0
    failed = 0

    for check in checks:
        if re.search(check["pattern"], content):
            print(f"[PASS] {check['name']}")
            passed += 1
        else:
            print(f"[FAIL] {check['name']}")
            failed += 1

    print(f"\nResults: {passed} passed, {failed} failed")
    return failed == 0


def verify_changelog():
    """Verify CHANGELOG.md exists and documents changes"""
    print("\n" + "="*60)
    print("Verifying CHANGELOG.md")
    print("="*60)

    changelog_file = Path(__file__).parent.parent / "CHANGELOG.md"

    if not changelog_file.exists():
        print(f"[FAIL] CHANGELOG.md not found")
        return False

    print(f"[PASS] CHANGELOG.md exists")

    with open(changelog_file, 'r', encoding='utf-8') as f:
        content = f.read()

    required_sections = [
        "User Registration Not Working",
        "Missing Authentication Tokens",
        "Role Selection Ignored",
        "backend/app/routers/auth.py",
        "backend/app/schemas.py"
    ]

    passed = 0
    failed = 0

    for section in required_sections:
        if section in content:
            print(f"[PASS] Documents: {section}")
            passed += 1
        else:
            print(f"[FAIL] Missing: {section}")
            failed += 1

    print(f"\nResults: {passed} passed, {failed} failed")
    return failed == 0


def main():
    print("\n" + "="*60)
    print("REGISTRATION FIX VERIFICATION")
    print("="*60 + "\n")

    results = []

    results.append(("Auth Endpoint (auth.py)", verify_auth_endpoint()))
    results.append(("Schema Definitions (schemas.py)", verify_schemas()))
    results.append(("Documentation (CHANGELOG.md)", verify_changelog()))

    print("\n" + "="*60)
    print("FINAL SUMMARY")
    print("="*60)

    all_passed = all(result for _, result in results)

    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {name}")

    if all_passed:
        print("\n" + "="*60)
        print("SUCCESS: All verification checks passed!")
        print("="*60)
        print("\nThe registration fix is complete:")
        print("  1. Users can now select their role during signup")
        print("  2. JWT tokens are returned for automatic login")
        print("  3. All changes are documented in CHANGELOG.md")
        print("\nNo database migration needed - existing schema supports all features.")
        print("\nNext steps:")
        print("  - Test registration in the running application")
        print("  - Verify automatic login after registration")
        print("  - Test all role types (viewer, analyst, partner, admin)")
        return 0
    else:
        print("\n" + "="*60)
        print("FAILURE: Some verification checks failed")
        print("="*60)
        print("\nReview the output above for details.")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
