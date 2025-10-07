#!/usr/bin/env python3
"""
AIAlchemy - Verify Admin User Creation
Checks if the admin user was created successfully in Supabase
"""

import os
import asyncio
from supabase import create_client, Client

async def verify_admin_user():
    """Verify admin user exists in Supabase"""
    
    # Get Supabase credentials from environment
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_ANON_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ Missing Supabase credentials!")
        print("   Set SUPABASE_URL and SUPABASE_ANON_KEY environment variables")
        return False
    
    try:
        # Create Supabase client
        supabase: Client = create_client(supabase_url, supabase_key)
        
        print("🔍 Checking for admin user...")
        
        # Query users table
        response = supabase.table('users').select('*').eq('email', 'admin@aialchemy.com').execute()
        
        if response.data:
            user = response.data[0]
            print("✅ Admin user found!")
            print(f"   Email: {user['email']}")
            print(f"   Username: {user['username']}")
            print(f"   Full Name: {user['full_name']}")
            print(f"   Active: {user['is_active']}")
            print(f"   Superuser: {user['is_superuser']}")
            print(f"   Created: {user['created_at']}")
            return True
        else:
            print("❌ Admin user not found!")
            print("   Execute create_admin_user.sql in Supabase SQL Editor")
            return False
            
    except Exception as e:
        print(f"❌ Error checking admin user: {e}")
        return False

def main():
    print("AIAlchemy - Admin User Verification")
    print("="*37)
    
    # Run verification
    result = asyncio.run(verify_admin_user())
    
    if result:
        print(f"\n🎉 Admin user is ready!")
        print(f"🔐 Login at your app with:")
        print(f"   Email: admin@aialchemy.com") 
        print(f"   Password: admin123")
        print(f"\n⚠️  SECURITY: Change password after first login!")
    else:
        print(f"\n📋 Next Steps:")
        print(f"   1. Run create_admin_user.sql in Supabase SQL Editor")
        print(f"   2. Or run: python3 create_custom_admin.py")

if __name__ == "__main__":
    main()