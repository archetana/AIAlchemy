#!/usr/bin/env python3
"""
Test Supabase Connection and Operations
"""

import os
import asyncio
from dotenv import load_dotenv
from app.core.supabase_client import get_supabase_client
from app.services.database_service import db_service

async def test_supabase_connection():
    """Test Supabase connection and basic operations"""
    
    # Load environment variables
    load_dotenv()
    
    print("🧪 Testing Supabase Connection...")
    
    # Test 1: Basic connection
    try:
        supabase = get_supabase_client()
        print("✅ Supabase client created successfully")
    except Exception as e:
        print(f"❌ Failed to create Supabase client: {e}")
        return False
    
    # Test 2: Check if tables exist
    try:
        result = supabase.table('startup_applications').select('id').limit(1).execute()
        print("✅ Successfully queried startup_applications table")
    except Exception as e:
        print(f"❌ Failed to query startup_applications table: {e}")
        print("💡 You may need to run database migrations first")
        return False
    
    # Test 3: Test database service
    try:
        # Set to use Supabase for this test
        os.environ['USE_SUPABASE'] = 'true'
        
        # Create test startup
        test_data = {
            "company_name": "Test Supabase Company",
            "contact_email": "test@supabase-test.com",
            "contact_name": "Test User",
            "website": "https://test-supabase.com",
            "industry_id": 1,
            "funding_stage": "seed",
            "funding_amount_requested": 1000000,
            "status": "new"
        }
        
        result = await db_service.create_startup(test_data)
        print(f"✅ Successfully created test startup: {result}")
        
        # Get the created startup
        if result.get('data') and result['data'].get('id'):
            startup_id = result['data']['id']
            
            # Test get
            startup = await db_service.get_startup(startup_id)
            print(f"✅ Successfully retrieved startup: {startup['company_name']}")
            
            # Test update
            update_result = await db_service.update_startup(
                startup_id, 
                {"company_name": "Updated Supabase Company"}
            )
            print(f"✅ Successfully updated startup: {update_result}")
            
            # Test list
            startups = await db_service.list_startups(page=1, page_size=5)
            print(f"✅ Successfully listed startups: {len(startups['items'])} items")
            
        return True
        
    except Exception as e:
        print(f"❌ Database service test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Supabase Integration Test")
    print("=" * 40)
    
    # Check environment variables
    required_vars = ["SUPABASE_URL", "SUPABASE_ANON_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please set these in your .env file:")
        for var in missing_vars:
            print(f"  {var}=your_value_here")
        return False
    
    # Run tests
    success = asyncio.run(test_supabase_connection())
    
    if success:
        print("\n🎉 All Supabase tests passed!")
        print("You can now use Supabase as your database backend.")
    else:
        print("\n💥 Some tests failed.")
        print("Check the error messages above and fix the issues.")
    
    return success

if __name__ == "__main__":
    main()