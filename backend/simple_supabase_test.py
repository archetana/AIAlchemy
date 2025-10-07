#!/usr/bin/env python3
"""
Simple Supabase IPv4 Connection Test
Tests the fixed Supabase client with IPv4-only resolution
"""

import os
import socket
from dotenv import load_dotenv

def force_ipv4_globally():
    """Force all socket connections to use IPv4 only"""
    original_getaddrinfo = socket.getaddrinfo
    
    def ipv4_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
        return original_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)
    
    socket.getaddrinfo = ipv4_getaddrinfo
    print("🔧 Configured IPv4-only DNS resolution globally")

def test_supabase_ipv4():
    """Test Supabase connection with IPv4 configuration"""
    
    print("🚀 Simple Supabase IPv4 Test")
    print("=" * 40)
    
    # Load environment
    load_dotenv()
    
    # Force IPv4 globally
    force_ipv4_globally()
    
    # Test 1: Basic connection test
    print("1️⃣ Testing basic Supabase client...")
    
    try:
        from supabase import create_client
        
        # Credentials
        supabase_url = "https://udjsdlfturbgiqnjsozo.supabase.co"
        supabase_anon_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVkanNkbGZ0dXJiZ2lxbmpzb3pvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk3ODgwNjMsImV4cCI6MjA3NTM2NDA2M30.vCfIXigCD2uUKZr5Y3cxYisVyn34DgZXd0QSUwgzr6Y"
        
        # Create client
        supabase = create_client(supabase_url, supabase_anon_key)
        print("   ✅ Client created successfully")
        
        # Test connection
        result = supabase.table('startup_applications').select('id').limit(1).execute()
        print(f"   ✅ Connection test successful: {len(result.data)} rows returned")
        
    except Exception as e:
        error_msg = str(e)
        if "Could not find the table" in error_msg:
            print("   ⚠️  Connection works, but table doesn't exist (expected)")
            print("   💡 Need to execute schema in Supabase Dashboard")
        else:
            print(f"   ❌ Connection failed: {e}")
            return False
    
    # Test 2: Our custom client manager
    print("\n2️⃣ Testing custom Supabase client manager...")
    
    try:
        # Set environment variables
        os.environ['SUPABASE_URL'] = "https://udjsdlfturbgiqnjsozo.supabase.co"
        os.environ['SUPABASE_ANON_KEY'] = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVkanNkbGZ0dXJiZ2lxbmpzb3pvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk3ODgwNjMsImV4cCI6MjA3NTM2NDA2M30.vCfIXigCD2uUKZr5Y3cxYisVyn34DgZXd0QSUwgzr6Y"
        
        from app.core.supabase_client import get_supabase_client
        
        client = get_supabase_client()
        print("   ✅ Custom client manager works")
        
        # Test connection
        result = client.table('startup_applications').select('id').limit(1).execute()
        print(f"   ✅ Custom client connection successful")
        
    except Exception as e:
        error_msg = str(e)
        if "Could not find the table" in error_msg:
            print("   ⚠️  Custom client works, table doesn't exist (expected)")
        else:
            print(f"   ❌ Custom client failed: {e}")
            return False
    
    print("\n🎉 All IPv4 tests passed!")
    print("\n📋 Next steps:")
    print("1. Execute database schema in Supabase Dashboard")
    print("2. Go to: https://supabase.com/dashboard")
    print("3. Open project: udjsdlfturbgiqnjsozo")
    print("4. Navigate to 'SQL Editor'")
    print("5. Copy and paste backend/supabase_schema.sql")
    print("6. Click 'Run' to create all tables")
    
    return True

if __name__ == "__main__":
    success = test_supabase_ipv4()
    if success:
        print("\n✅ IPv4 Supabase integration is working!")
    else:
        print("\n❌ IPv4 tests failed - check network and credentials")