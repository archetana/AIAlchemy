#!/usr/bin/env python3
"""
Create Tables Using Supabase REST API
Creates essential tables one by one using Supabase client
"""

import os
from supabase import create_client, Client

def create_essential_tables():
    """Create essential tables using Supabase REST API approach"""
    
    # Supabase credentials
    supabase_url = "https://udjsdlfturbgiqnjsozo.supabase.co"
    supabase_anon_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVkanNkbGZ0dXJiZ2lxbmpzb3pvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk3ODgwNjMsImV4cCI6MjA3NTM2NDA2M30.vCfIXigCD2uUKZr5Y3cxYisVyn34DgZXd0QSUwgzr6Y"
    
    print("🗄️ Creating Essential Tables in Supabase...")
    print("=" * 50)
    
    # Create Supabase client
    supabase: Client = create_client(supabase_url, supabase_anon_key)
    
    # Since we can't execute raw SQL, let's try to create a test record
    # to see if tables exist or get more information
    
    print("🔍 Testing Supabase connection and table access...")
    
    try:
        # Test 1: Try to query a table that should exist
        result = supabase.table('startup_applications').select('*').limit(1).execute()
        print("✅ startup_applications table exists!")
        print(f"📊 Current records: {len(result.data)}")
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ startup_applications table error: {error_msg}")
        
        if "Could not find the table" in error_msg:
            print("\n📋 The tables don't exist yet.")
            print("📝 Manual schema execution is required.")
            print("\n🔧 SOLUTION: Execute the schema manually in Supabase Dashboard:")
            print("1. Go to https://supabase.com/dashboard")
            print("2. Open project: udjsdlfturbgiqnjsozo") 
            print("3. Go to 'SQL Editor'")
            print("4. Copy the entire contents of 'supabase_schema.sql'")
            print("5. Paste and execute in SQL Editor")
            
            print("\n📄 Schema file location: backend/supabase_schema.sql")
            print("📄 Contains: Tables, enums, indexes, triggers, and RLS policies")
            
            return False
    
    # Test other tables if startup_applications exists
    tables_to_test = [
        'industries',
        'users', 
        'founders',
        'uploaded_files',
        'financial_metrics'
    ]
    
    for table_name in tables_to_test:
        try:
            result = supabase.table(table_name).select('*').limit(1).execute()
            print(f"✅ {table_name} table exists with {len(result.data)} records")
        except Exception as e:
            print(f"❌ {table_name} table error: {str(e)[:100]}...")
    
    return True

def test_table_operations():
    """Test basic CRUD operations on tables"""
    
    # Supabase credentials
    supabase_url = "https://udjsdlfturbgiqnjsozo.supabase.co"
    supabase_anon_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVkanNkbGZ0dXJiZ2lxbmpzb3pvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk3ODgwNjMsImV4cCI6MjA3NTM2NDA2M30.vCfIXigCD2uUKZr5Y3cxYisVyn34DgZXd0QSUwgzr6Y"
    
    print("\n🧪 Testing Table Operations...")
    print("=" * 40)
    
    # Create Supabase client
    supabase: Client = create_client(supabase_url, supabase_anon_key)
    
    try:
        # Test creating a startup application
        test_data = {
            "company_name": "Test Company",
            "contact_email": "test@example.com", 
            "contact_name": "Test User",
            "website": "https://test.com",
            "industry_id": 1,
            "funding_stage": "seed",
            "status": "new"
        }
        
        print("🔬 Testing startup application creation...")
        result = supabase.table('startup_applications').insert(test_data).execute()
        
        if result.data:
            print("✅ Successfully created test startup application!")
            startup_id = result.data[0]['id']
            print(f"📋 Created startup ID: {startup_id}")
            
            # Test reading it back
            read_result = supabase.table('startup_applications').select('*').eq('id', startup_id).execute()
            if read_result.data:
                print("✅ Successfully read back the created startup!")
            
            # Clean up - delete the test record
            delete_result = supabase.table('startup_applications').delete().eq('id', startup_id).execute()
            print("🧹 Cleaned up test record")
            
        return True
        
    except Exception as e:
        print(f"❌ Table operation test failed: {e}")
        return False

if __name__ == "__main__":
    # Step 1: Check if tables exist
    tables_exist = create_essential_tables()
    
    # Step 2: If tables exist, test operations
    if tables_exist:
        test_table_operations()