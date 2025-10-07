#!/usr/bin/env python3
"""
AIAlchemy - Create User via API
Creates a new user account using the registration API endpoint
"""

import requests
import json
import sys

def create_user_via_api(base_url: str, user_data: dict):
    """Create user via API registration endpoint"""
    
    registration_url = f"{base_url}/api/v1/auth/register"
    
    try:
        print(f"🔗 Sending request to: {registration_url}")
        print(f"📋 User data: {json.dumps(user_data, indent=2)}")
        
        response = requests.post(
            registration_url,
            json=user_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"📡 Response Status: {response.status_code}")
        print(f"📄 Response Body: {response.text}")
        
        if response.status_code == 201:
            print("✅ User created successfully!")
            return response.json()
        else:
            print(f"❌ Failed to create user: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return None

def main():
    print("AIAlchemy - Create User via API")
    print("="*35)
    
    # Configuration
    base_url = input("API Base URL (e.g., https://your-app.run.app): ").strip()
    if not base_url:
        base_url = "http://localhost:8000"  # Default for local development
    
    print(f"\n🌐 Using API: {base_url}")
    
    # User data
    user_data = {
        "email": input("Email: ").strip(),
        "username": input("Username: ").strip(),  
        "full_name": input("Full Name: ").strip(),
        "password": input("Password: ").strip()
    }
    
    if not all(user_data.values()):
        print("❌ All fields are required!")
        sys.exit(1)
    
    # Create user
    result = create_user_via_api(base_url, user_data)
    
    if result:
        print(f"\n🎉 User created successfully!")
        print(f"📧 Login with: {user_data['email']} / {user_data['password']}")
    else:
        print(f"\n💡 Alternative: Use SQL method instead")
        print(f"   Run: python3 create_custom_admin.py")

if __name__ == "__main__":
    main()