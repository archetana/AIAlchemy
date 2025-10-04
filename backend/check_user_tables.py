#!/usr/bin/env python3
"""
Check user table existence and data in AIAlchemy database
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

async def check_database_connection():
    """Test database connection"""
    try:
        print("🔌 Testing database connection...")
        from app.core.database import database_manager
        
        await database_manager.connect()
        
        if database_manager.is_connected:
            print("✅ Database connection successful")
            return True
        else:
            print("❌ Database connection failed")
            return False
            
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return False

async def check_user_table_exists():
    """Check if users table exists"""
    try:
        print("\n🔍 Checking if 'users' table exists...")
        from app.core.database import database_manager
        from sqlalchemy import text
        
        async with database_manager.get_session() as session:
            # Check if table exists in PostgreSQL
            result = await session.execute(
                text("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = 'users'
                    );
                """)
            )
            exists = result.scalar()
            
            if exists:
                print("✅ 'users' table exists")
                return True
            else:
                print("❌ 'users' table does not exist")
                return False
                
    except Exception as e:
        print(f"❌ Error checking users table: {e}")
        return False

async def check_user_table_schema():
    """Check users table schema"""
    try:
        print("\n📋 Checking 'users' table schema...")
        from app.core.database import database_manager
        from sqlalchemy import text
        
        async with database_manager.get_session() as session:
            result = await session.execute(
                text("""
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns 
                    WHERE table_name = 'users' 
                    AND table_schema = 'public'
                    ORDER BY ordinal_position;
                """)
            )
            columns = result.fetchall()
            
            if columns:
                print("📊 Users table schema:")
                print("+" + "-" * 70 + "+")
                print(f"| {'Column Name':<20} | {'Data Type':<15} | {'Nullable':<8} | {'Default':<18} |")
                print("+" + "-" * 70 + "+")
                
                for col in columns:
                    column_name, data_type, is_nullable, column_default = col
                    default_str = str(column_default)[:18] if column_default else "NULL"
                    print(f"| {column_name:<20} | {data_type:<15} | {is_nullable:<8} | {default_str:<18} |")
                
                print("+" + "-" * 70 + "+")
                return True
            else:
                print("❌ No schema information found for users table")
                return False
                
    except Exception as e:
        print(f"❌ Error checking users table schema: {e}")
        return False

async def check_user_table_data():
    """Check users table data"""
    try:
        print("\n👥 Checking 'users' table data...")
        from app.core.database import database_manager
        from sqlalchemy import text
        
        async with database_manager.get_session() as session:
            # Count users
            count_result = await session.execute(text("SELECT COUNT(*) FROM users"))
            user_count = count_result.scalar()
            
            print(f"📊 Total users in database: {user_count}")
            
            if user_count > 0:
                # Get sample users
                result = await session.execute(
                    text("SELECT id, email, full_name, role, is_active, created_at FROM users LIMIT 5")
                )
                users = result.fetchall()
                
                print("\n🔍 Sample users (first 5):")
                print("+" + "-" * 100 + "+")
                print(f"| {'ID':<3} | {'Email':<25} | {'Full Name':<20} | {'Role':<10} | {'Active':<6} | {'Created':<20} |")
                print("+" + "-" * 100 + "+")
                
                for user in users:
                    user_id, email, full_name, role, is_active, created_at = user
                    created_str = created_at.strftime("%Y-%m-%d %H:%M") if created_at else "N/A"
                    print(f"| {user_id:<3} | {email:<25} | {full_name:<20} | {role or 'N/A':<10} | {is_active:<6} | {created_str:<20} |")
                
                print("+" + "-" * 100 + "+")
            else:
                print("⚠️ No users found in database")
                
            return user_count > 0
                
    except Exception as e:
        print(f"❌ Error checking users table data: {e}")
        return False

async def check_all_tables():
    """Check what tables exist in the database"""
    try:
        print("\n📊 Checking all tables in database...")
        from app.core.database import database_manager
        from sqlalchemy import text
        
        async with database_manager.get_session() as session:
            result = await session.execute(
                text("""
                    SELECT table_name
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                    ORDER BY table_name;
                """)
            )
            tables = result.fetchall()
            
            if tables:
                print("📋 Existing tables:")
                for i, (table_name,) in enumerate(tables, 1):
                    print(f"  {i}. {table_name}")
            else:
                print("❌ No tables found in database")
                
            return len(tables) > 0
                
    except Exception as e:
        print(f"❌ Error checking database tables: {e}")
        return False

async def suggest_fixes():
    """Suggest fixes for missing user functionality"""
    print("\n💡 DIAGNOSIS AND RECOMMENDATIONS:")
    print("=" * 60)
    
    # Check database connection
    connected = await check_database_connection()
    if not connected:
        print("\n🔧 FIX REQUIRED:")
        print("1. Check DATABASE_URL environment variable")
        print("2. Ensure PostgreSQL database is running")
        print("3. Verify database credentials")
        return
    
    # Check all tables
    tables_exist = await check_all_tables()
    
    # Check user table specifically
    user_table_exists = await check_user_table_exists()
    
    if not user_table_exists:
        print("\n🔧 CRITICAL FIX REQUIRED:")
        print("❌ The 'users' table does not exist!")
        print("\n💻 Run these commands to fix:")
        print("1. cd /home/agenticai/webapp/backend")
        print("2. python init_database.py")
        print("   OR")
        print("3. alembic upgrade head")
        
        if not tables_exist:
            print("\n⚠️ NO TABLES FOUND - Database appears to be completely empty!")
            print("This explains why the API returns 'User not found'")
    else:
        await check_user_table_schema()
        has_users = await check_user_table_data()
        
        if not has_users:
            print("\n🔧 FIX REQUIRED:")
            print("❌ Users table exists but is EMPTY!")
            print("\n💻 To fix this issue:")
            print("1. Create a default user in the database")
            print("2. Or modify the API to handle missing users gracefully")
            print("3. Or implement proper user registration/login")
        else:
            print("\n✅ Users table exists and has data")
            print("🔍 The API error might be due to:")
            print("  - Missing authentication headers")
            print("  - Invalid user ID in JWT token")  
            print("  - API trying to find user that doesn't exist")
    
    # Disconnect from database
    try:
        from app.core.database import database_manager
        await database_manager.disconnect()
    except:
        pass

async def main():
    """Main function"""
    print("🔍 AIAlchemy Database User Table Checker")
    print("=" * 50)
    
    await suggest_fixes()

if __name__ == "__main__":
    asyncio.run(main())