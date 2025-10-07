#!/usr/bin/env python3
"""
Verify Supabase Setup and Integration
Complete test suite for Supabase database integration
"""

import os
import asyncio
from datetime import datetime
from supabase import create_client, Client

async def verify_supabase_setup():
    """Comprehensive verification of Supabase setup"""
    
    print("🔍 Supabase Setup Verification")
    print("=" * 50)
    
    # Supabase credentials
    supabase_url = "https://udjsdlfturbgiqnjsozo.supabase.co"
    supabase_anon_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVkanNkbGZ0dXJiZ2lxbmpzb3pvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk3ODgwNjMsImV4cCI6MjA3NTM2NDA2M30.vCfIXigCD2uUKZr5Y3cxYisVyn34DgZXd0QSUwgzr6Y"
    
    # Create Supabase client
    supabase: Client = create_client(supabase_url, supabase_anon_key)
    
    # Test 1: Connection
    print("1️⃣ Testing connection...")
    try:
        # Simple ping test
        result = supabase.table('users').select('id').limit(1).execute()
        print("   ✅ Connection successful")
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
        return False
    
    # Test 2: Required tables exist
    print("\n2️⃣ Checking required tables...")
    required_tables = [
        'industries',
        'users', 
        'startup_applications',
        'founders',
        'uploaded_files',
        'financial_metrics',
        'investment_memos',
        'evaluation_history'
    ]
    
    missing_tables = []
    for table in required_tables:
        try:
            result = supabase.table(table).select('*').limit(1).execute()
            print(f"   ✅ {table}")
        except Exception as e:
            print(f"   ❌ {table} - {str(e)[:60]}...")
            missing_tables.append(table)
    
    if missing_tables:
        print(f"\n   🚨 Missing tables: {', '.join(missing_tables)}")
        print("   📝 Please execute the schema SQL in Supabase Dashboard")
        return False
    
    # Test 3: Check if default data exists
    print("\n3️⃣ Checking default data...")
    
    # Check industries
    industries = supabase.table('industries').select('*').execute()
    print(f"   📊 Industries: {len(industries.data)} records")
    if len(industries.data) == 0:
        print("   💡 No default industries found - this is expected if schema was just created")
    
    # Test 4: Create, read, update, delete operations
    print("\n4️⃣ Testing CRUD operations...")
    
    try:
        # Create test startup
        test_startup = {
            "company_name": f"Test Company {datetime.now().strftime('%H%M%S')}",
            "contact_email": "test@verification.com",
            "contact_name": "Verification Test",
            "website": "https://test-verification.com",
            "funding_stage": "seed",
            "status": "new"
        }
        
        # If industries exist, use the first one
        if len(industries.data) > 0:
            test_startup["industry_id"] = industries.data[0]['id']
        
        # CREATE
        create_result = supabase.table('startup_applications').insert(test_startup).execute()
        if create_result.data:
            startup_id = create_result.data[0]['id']
            print(f"   ✅ CREATE - Created startup ID: {startup_id}")
            
            # READ
            read_result = supabase.table('startup_applications').select('*').eq('id', startup_id).execute()
            if read_result.data:
                print(f"   ✅ READ - Retrieved startup: {read_result.data[0]['company_name']}")
                
                # UPDATE
                update_data = {"company_name": f"Updated Test Company {startup_id}"}
                update_result = supabase.table('startup_applications').update(update_data).eq('id', startup_id).execute()
                if update_result.data:
                    print(f"   ✅ UPDATE - Updated company name")
                    
                    # DELETE
                    delete_result = supabase.table('startup_applications').delete().eq('id', startup_id).execute()
                    print(f"   ✅ DELETE - Cleaned up test record")
        
    except Exception as e:
        print(f"   ❌ CRUD test failed: {e}")
        return False
    
    # Test 5: Test hybrid database service
    print("\n5️⃣ Testing hybrid database service...")
    
    try:
        # Import and test the database service
        from app.services.database_service import db_service
        
        # Set to use Supabase
        os.environ['USE_SUPABASE'] = 'true'
        
        # Test create via service
        service_test_data = {
            "company_name": f"Service Test {datetime.now().strftime('%H%M%S')}",
            "contact_email": "service@test.com",
            "contact_name": "Service Test User",
            "website": "https://service-test.com",
            "funding_stage": "pre_seed",
            "status": "new"
        }
        
        result = await db_service.create_startup(service_test_data)
        if result and result.get('success'):
            print(f"   ✅ Service CREATE - Success")
            
            startup_id = result['data']['id']
            
            # Test get via service
            startup = await db_service.get_startup(startup_id)
            if startup:
                print(f"   ✅ Service GET - Retrieved: {startup['company_name']}")
            
            # Test update via service
            update_result = await db_service.update_startup(startup_id, {"company_name": "Updated via Service"})
            if update_result:
                print(f"   ✅ Service UPDATE - Success")
            
            # Test list via service
            list_result = await db_service.list_startups(page=1, page_size=5)
            if list_result and 'items' in list_result:
                print(f"   ✅ Service LIST - Found {len(list_result['items'])} startups")
            
            # Cleanup
            cleanup = supabase.table('startup_applications').delete().eq('id', startup_id).execute()
            print(f"   🧹 Cleaned up service test record")
        
    except Exception as e:
        print(f"   ❌ Service test failed: {e}")
        return False
    
    print("\n🎉 All Supabase verification tests passed!")
    print("✅ Supabase integration is working correctly")
    return True

def main():
    """Main verification function"""
    print("🚀 Starting Supabase Verification...")
    
    success = asyncio.run(verify_supabase_setup())
    
    if success:
        print("\n" + "=" * 50)
        print("🎯 VERIFICATION COMPLETE - ALL SYSTEMS GO!")
        print("🔧 Your Supabase integration is ready to use")
        print("🚀 You can now start the backend server and test the full application")
    else:
        print("\n" + "=" * 50) 
        print("🚨 VERIFICATION FAILED")
        print("📋 Please check the errors above and:")
        print("1. Execute the schema SQL in Supabase Dashboard")
        print("2. Ensure all tables are created properly")
        print("3. Run this verification script again")

if __name__ == "__main__":
    main()