#!/usr/bin/env python3
"""
Database Configuration Diagnostic Tool
Helps debug why SQLite vs Supabase is being selected
"""

import os
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent))

def diagnose_database_config():
    """Diagnose database configuration issues"""
    
    print("🔍 AIAlchemy Database Configuration Diagnosis")
    print("=" * 60)
    
    # Check environment variables
    print("\n📋 Environment Variables:")
    env_vars = [
        "USE_SUPABASE",
        "SUPABASE_URL", 
        "SUPABASE_ANON_KEY",
        "DATABASE_URL",
        "ENVIRONMENT"
    ]
    
    for var in env_vars:
        value = os.getenv(var, "NOT_SET")
        if var in ["SUPABASE_ANON_KEY"] and value != "NOT_SET":
            # Mask sensitive data
            masked_value = value[:10] + "..." + value[-4:] if len(value) > 14 else "***"
            print(f"   {var}: {masked_value}")
        elif var in ["SUPABASE_URL"] and value != "NOT_SET":
            # Show partial URL
            print(f"   {var}: {value[:30]}...")
        else:
            print(f"   {var}: {value}")
    
    # Test configuration loading
    print("\n⚙️ Configuration Loading Test:")
    try:
        from app.core.config import get_settings
        settings = get_settings()
        
        print(f"   ✅ Config loaded successfully")
        print(f"   Environment: {settings.environment}")
        print(f"   USE_SUPABASE: {settings.use_supabase}")
        print(f"   should_use_supabase: {settings.should_use_supabase}")
        print(f"   Supabase URL: {'✅ Set' if settings.supabase_url else '❌ Missing'}")
        print(f"   Supabase Key: {'✅ Set' if settings.supabase_anon_key else '❌ Missing'}")
        
    except Exception as e:
        print(f"   ❌ Config loading failed: {e}")
        return False
    
    # Test database service
    print("\n🗄️ Database Service Test:")
    try:
        from app.services.database_service import db_service
        
        print(f"   Database service initialized: {'✅ Yes' if db_service else '❌ No'}")
        print(f"   Using Supabase: {'✅ Yes' if db_service.use_supabase else '❌ No (using SQLAlchemy)'}")
        
        if db_service.use_supabase:
            print(f"   Supabase client: {'✅ Available' if hasattr(db_service, 'supabase') else '❌ Not initialized'}")
    except Exception as e:
        print(f"   ❌ Database service test failed: {e}")
        return False
    
    # Test Supabase connection if configured
    if settings.should_use_supabase:
        print("\n🔗 Supabase Connection Test:")
        try:
            from app.core.supabase_client import get_supabase_client
            supabase = get_supabase_client()
            
            # Test basic query
            result = supabase.table('users').select('count').limit(1).execute()
            print(f"   ✅ Supabase connection successful")
            print(f"   Response data: {len(result.data) if result.data else 0} items")
            
        except Exception as e:
            print(f"   ❌ Supabase connection failed: {e}")
            return False
    
    # Test database factory
    print("\n🏭 Database Factory Test:")
    try:
        from app.core.database_factory import database_factory
        
        db_info = database_factory.get_database_info()
        print(f"   Backend: {db_info['backend']}")
        print(f"   Environment: {db_info['environment']}")
        print(f"   Auto-detected: {db_info['auto_detected']}")
        print(f"   Connection status: {db_info['connection_status']}")
        
    except Exception as e:
        print(f"   ❌ Database factory test failed: {e}")
        return False
    
    # Summary and recommendations
    print(f"\n📊 Summary:")
    if settings.should_use_supabase:
        print(f"   🎯 Expected behavior: Should use Supabase")
        if db_service.use_supabase:
            print(f"   ✅ Current behavior: Using Supabase correctly")
        else:
            print(f"   ❌ Current behavior: Using SQLAlchemy (PROBLEM!)")
    else:
        print(f"   🎯 Expected behavior: Should use SQLAlchemy")
        if not db_service.use_supabase:
            print(f"   ✅ Current behavior: Using SQLAlchemy correctly")
        else:
            print(f"   ❌ Current behavior: Using Supabase (unexpected)")
    
    print(f"\n💡 Recommendations:")
    
    if not settings.should_use_supabase and settings.environment in ["production", "staging"]:
        print(f"   🔧 Set SUPABASE_URL and SUPABASE_ANON_KEY environment variables")
        print(f"   🔧 Or set USE_SUPABASE=true to force Supabase usage")
    
    if settings.should_use_supabase and not db_service.use_supabase:
        print(f"   🔧 Database service is not respecting Supabase configuration")
        print(f"   🔧 Check app/services/database_service.py initialization")
    
    if not settings.supabase_url and settings.environment == "production":
        print(f"   ⚠️  Production environment without Supabase configuration detected")
        print(f"   🔧 Add GitHub Secrets: SUPABASE_URL, SUPABASE_ANON_KEY")
    
    return True

def main():
    """Main diagnostic function"""
    try:
        success = diagnose_database_config()
        
        if success:
            print(f"\n✅ Diagnosis complete!")
        else:
            print(f"\n❌ Diagnosis failed - check errors above")
            
    except Exception as e:
        print(f"\n💥 Diagnostic tool failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()