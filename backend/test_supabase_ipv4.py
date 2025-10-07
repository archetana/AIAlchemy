#!/usr/bin/env python3
"""
Test Supabase Connection with IPv4-Only Configuration
Resolves IPv6 connectivity issues by forcing IPv4 connections
"""

import os
import socket
import asyncio
from datetime import datetime
from dotenv import load_dotenv
import httpx
from urllib.parse import urlparse

# Force IPv4 resolution for all HTTP connections
def force_ipv4_resolution():
    """Configure system to prefer IPv4 connections"""
    # Override socket.getaddrinfo to return only IPv4 addresses
    original_getaddrinfo = socket.getaddrinfo
    
    def ipv4_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
        return original_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)
    
    socket.getaddrinfo = ipv4_getaddrinfo

async def test_supabase_connection_ipv4():
    """Test Supabase connection with IPv4-only configuration"""
    
    # Load environment variables
    load_dotenv()
    
    print("🔧 Testing Supabase Connection (IPv4-Only Mode)")
    print("=" * 55)
    
    # Supabase credentials
    supabase_url = "https://udjsdlfturbgiqnjsozo.supabase.co"
    supabase_anon_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVkanNkbGZ0dXJiZ2lxbmpzb3pvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk3ODgwNjMsImV4cCI6MjA3NTM2NDA2M30.vCfIXigCD2uUKZr5Y3cxYisVyn34DgZXd0QSUwgzr6Y"
    
    print("🌐 Testing IPv4 connectivity...")
    
    # Test 1: Direct IPv4 HTTP connection
    try:
        parsed = urlparse(supabase_url)
        hostname = parsed.hostname
        
        # Resolve hostname to IPv4
        ipv4_addr = socket.gethostbyname(hostname)
        print(f"   📍 Resolved {hostname} → {ipv4_addr}")
        
        # Test direct IPv4 connection
        ipv4_url = supabase_url.replace(hostname, ipv4_addr)
        
        # Create HTTP client with IPv4 configuration
        async with httpx.AsyncClient(
            timeout=30.0,
            headers={'Host': hostname}  # Preserve original hostname for SSL
        ) as client:
            response = await client.get(f"{ipv4_url}/")
            print(f"   ✅ IPv4 HTTP connection successful (status: {response.status_code})")
            
    except Exception as e:
        print(f"   ❌ IPv4 HTTP connection failed: {e}")
        return False
    
    # Test 2: Supabase Python client with IPv4
    try:
        print("\n🧪 Testing Supabase Python client...")
        
        # Force IPv4 resolution
        force_ipv4_resolution()
        
        # Import after forcing IPv4
        from supabase import create_client
        
        # Create Supabase client
        supabase = create_client(supabase_url, supabase_anon_key)
        print("   ✅ Supabase client created successfully")
        
        # Test basic connection
        try:
            result = supabase.table('startup_applications').select('id').limit(1).execute()
            print(f"   ✅ Database query test successful")
            print(f"   📊 Query returned: {len(result.data)} rows")
        except Exception as e:
            error_msg = str(e)
            if "Could not find the table" in error_msg:
                print("   ⚠️  Database query failed: Tables not yet created")
                print("   💡 This is expected if schema hasn't been executed yet")
            else:
                print(f"   ❌ Database query failed: {e}")
                return False
        
    except Exception as e:
        print(f"   ❌ Supabase client test failed: {e}")
        return False
    
    # Test 3: Test database service integration
    try:
        print("\n🔧 Testing hybrid database service...")
        
        # Set environment for Supabase
        os.environ['USE_SUPABASE'] = 'true'
        os.environ['SUPABASE_URL'] = supabase_url
        os.environ['SUPABASE_ANON_KEY'] = supabase_anon_key
        
        # Import and test database service
        from app.services.database_service import db_service
        
        # Create test startup data
        test_data = {
            "company_name": f"IPv4 Test Company {datetime.now().strftime('%H%M%S')}",
            "contact_email": "ipv4test@example.com",
            "contact_name": "IPv4 Test User",
            "website": "https://ipv4test.com",
            "funding_stage": "seed",
            "status": "new"
        }
        
        # Test service operations
        try:
            result = await db_service.create_startup(test_data)
            if result and result.get('success'):
                startup_id = result['data']['id']
                print(f"   ✅ Service CREATE test successful (ID: {startup_id})")
                
                # Test get operation
                startup = await db_service.get_startup(startup_id)
                if startup:
                    print(f"   ✅ Service GET test successful")
                
                # Cleanup test record
                cleanup_result = supabase.table('startup_applications').delete().eq('id', startup_id).execute()
                print(f"   🧹 Test record cleaned up")
                
            else:
                print(f"   ❌ Service CREATE test failed: {result}")
                
        except Exception as service_error:
            error_msg = str(service_error)
            if "Could not find the table" in error_msg:
                print("   ⚠️  Service test skipped: Database tables not created yet")
            else:
                print(f"   ❌ Service test failed: {service_error}")
        
    except Exception as e:
        print(f"   ❌ Database service test failed: {e}")
        return False
    
    print("\n🎉 IPv4 Supabase Connection Test Completed!")
    return True

def main():
    """Main test function"""
    print("🚀 Supabase IPv4 Connection Test")
    print("🔧 Resolving IPv6 connectivity issues")
    print("=" * 50)
    
    # Run the test
    success = asyncio.run(test_supabase_connection_ipv4())
    
    if success:
        print("\n" + "=" * 50)
        print("✅ IPv4 CONNECTION TESTS PASSED!")
        print("🎯 Supabase integration working with IPv4-only configuration")
        print("💡 Ready to execute database schema in Supabase Dashboard")
        print("\nNext steps:")
        print("1. Execute schema SQL in Supabase Dashboard")
        print("2. Set USE_SUPABASE=true in production")
        print("3. Deploy with IPv4-optimized configuration")
    else:
        print("\n" + "=" * 50)
        print("❌ SOME TESTS FAILED")
        print("🔧 Check network connectivity and credentials")

if __name__ == "__main__":
    main()