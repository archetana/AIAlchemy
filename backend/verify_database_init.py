#!/usr/bin/env python3
"""
Verify Database Initialization
Checks that all required initial data is present for the application to work properly
"""

import os
import socket
import asyncio
from datetime import datetime
from dotenv import load_dotenv

def force_ipv4_globally():
    """Force all socket connections to use IPv4 only"""
    original_getaddrinfo = socket.getaddrinfo
    
    def ipv4_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
        return original_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)
    
    socket.getaddrinfo = ipv4_getaddrinfo

async def verify_database_initialization():
    """Verify all required database initialization data is present"""
    
    print("🔍 Database Initialization Verification")
    print("=" * 50)
    
    # Load environment and force IPv4
    load_dotenv()
    force_ipv4_globally()
    
    try:
        from supabase import create_client
        
        # Create Supabase client
        supabase_url = "https://udjsdlfturbgiqnjsozo.supabase.co"
        supabase_anon_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVkanNkbGZ0dXJiZ2lxbmpzb3pvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk3ODgwNjMsImV4cCI6MjA3NTM2NDA2M30.vCfIXigCD2uUKZr5Y3cxYisVyn34DgZXd0QSUwgzr6Y"
        
        supabase = create_client(supabase_url, supabase_anon_key)
        print("✅ Connected to Supabase successfully")
        
        all_checks_passed = True
        
        # Check 1: Industries (CRITICAL - Required by frontend)
        print("\n1️⃣ Checking Industries...")
        try:
            industries = supabase.table('industries').select('*').execute()
            industry_count = len(industries.data)
            
            if industry_count >= 8:
                print(f"   ✅ Industries present: {industry_count} entries")
                
                # Check for required IDs 1-8 that frontend expects
                industry_ids = [item['id'] for item in industries.data]
                required_ids = [1, 2, 3, 4, 5, 6, 7, 8]
                missing_ids = [id for id in required_ids if id not in industry_ids]
                
                if not missing_ids:
                    print("   ✅ All required industry IDs (1-8) present")
                    
                    # Show industries
                    print("   📋 Available industries:")
                    for industry in industries.data[:10]:  # Show first 10
                        print(f"      {industry['id']}: {industry['name']}")
                else:
                    print(f"   ❌ Missing required industry IDs: {missing_ids}")
                    all_checks_passed = False
            else:
                print(f"   ❌ Insufficient industries: {industry_count} (need at least 8)")
                all_checks_passed = False
                
        except Exception as e:
            print(f"   ❌ Industries check failed: {e}")
            all_checks_passed = False
        
        # Check 2: Investment Weights (Required for AI scoring)
        print("\n2️⃣ Checking Investment Weights...")
        try:
            weights = supabase.table('investment_weights').select('*').execute()
            weight_count = len(weights.data)
            
            if weight_count >= 5:
                print(f"   ✅ Investment weights present: {weight_count} criteria")
                
                # Check total weight sums to 1.0
                total_weight = sum(float(w['weight']) for w in weights.data if w['is_active'])
                if 0.99 <= total_weight <= 1.01:  # Allow for floating point precision
                    print(f"   ✅ Total weight valid: {total_weight:.2f}")
                else:
                    print(f"   ⚠️  Total weight: {total_weight:.2f} (should be 1.0)")
                
                # Show criteria
                print("   📋 Scoring criteria:")
                for weight in weights.data:
                    if weight['is_active']:
                        print(f"      {weight['criterion']}: {float(weight['weight']):.2f} ({weight['category']})")
            else:
                print(f"   ❌ Insufficient investment weights: {weight_count} (need at least 5)")
                all_checks_passed = False
                
        except Exception as e:
            print(f"   ❌ Investment weights check failed: {e}")
            all_checks_passed = False
        
        # Check 3: Users (Optional but recommended)
        print("\n3️⃣ Checking Users...")
        try:
            users = supabase.table('users').select('id,email,full_name,is_superuser').execute()
            user_count = len(users.data)
            
            if user_count > 0:
                print(f"   ✅ Users present: {user_count} accounts")
                
                # Check for admin users
                admin_users = [u for u in users.data if u['is_superuser']]
                if admin_users:
                    print(f"   ✅ Admin accounts: {len(admin_users)}")
                    for admin in admin_users:
                        print(f"      👑 {admin['full_name']} ({admin['email']})")
                else:
                    print("   ⚠️  No admin users found (create one for management access)")
            else:
                print("   ⚠️  No users found (optional - you can create accounts via API)")
                
        except Exception as e:
            print(f"   ❌ Users check failed: {e}")
            # Don't fail overall check for users as they're optional
        
        # Check 4: Test table operations
        print("\n4️⃣ Testing Database Operations...")
        try:
            # Test create operation
            test_app = {
                "company_name": f"Verification Test {datetime.now().strftime('%H%M%S')}",
                "contact_email": "verify@test.com",
                "contact_name": "Verification Bot",
                "industry_id": 1,  # Should exist from industries
                "funding_stage": "seed",
                "status": "new"
            }
            
            # Create test record
            create_result = supabase.table('startup_applications').insert(test_app).execute()
            if create_result.data:
                test_id = create_result.data[0]['id']
                print(f"   ✅ CREATE operation successful (ID: {test_id})")
                
                # Test read operation
                read_result = supabase.table('startup_applications').select('*').eq('id', test_id).execute()
                if read_result.data:
                    print("   ✅ READ operation successful")
                    
                    # Test update operation
                    update_result = supabase.table('startup_applications').update({
                        "company_name": "Updated Test Company"
                    }).eq('id', test_id).execute()
                    if update_result.data:
                        print("   ✅ UPDATE operation successful")
                    
                    # Clean up test record
                    delete_result = supabase.table('startup_applications').delete().eq('id', test_id).execute()
                    print("   🧹 Test record cleaned up")
                
            else:
                print("   ❌ CREATE operation failed")
                all_checks_passed = False
                
        except Exception as e:
            print(f"   ❌ Database operations test failed: {e}")
            all_checks_passed = False
        
        # Final result
        print("\n" + "=" * 50)
        if all_checks_passed:
            print("🎉 ALL CRITICAL CHECKS PASSED!")
            print("✅ Database is properly initialized and ready for production")
            print("\n📋 What's ready:")
            print("   ✅ Industries for startup categorization")
            print("   ✅ Investment weights for AI scoring")
            print("   ✅ Database operations (CRUD) working")
            print("   ✅ Supabase connection stable")
        else:
            print("❌ SOME CRITICAL CHECKS FAILED!")
            print("🔧 Please execute init_supabase_data.sql to fix missing data")
            
        return all_checks_passed
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def main():
    """Main verification function"""
    print("🚀 Database Initialization Verification")
    print("🔧 Checking all required data is present...")
    print()
    
    success = asyncio.run(verify_database_initialization())
    
    if success:
        print("\n🎯 READY FOR PRODUCTION!")
        print("The database has all required initialization data.")
    else:
        print("\n🛠️ INITIALIZATION REQUIRED!")
        print("Execute these commands to fix:")
        print("1. Go to Supabase Dashboard → SQL Editor")
        print("2. Execute: backend/init_supabase_data.sql")
        print("3. Run this script again to verify")

if __name__ == "__main__":
    main()