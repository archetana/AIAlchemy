#!/usr/bin/env python3
"""
Simple database check for AIAlchemy
"""

import os
import sqlite3

def check_sqlite_database():
    """Check the SQLite database directly"""
    print("🔍 Checking SQLite Database")
    print("=" * 50)
    
    # Get database path from env file
    db_path = "./aialchemy.db"
    
    print(f"📁 Database path: {db_path}")
    
    if not os.path.exists(db_path):
        print("❌ Database file does not exist!")
        print("🔧 This is likely why the API returns 'User not found'")
        print("\n💻 To fix this:")
        print("1. Run the database initialization script:")
        print("   python3 init_database.py")
        print("2. Or check if migrations need to be run:")
        print("   alembic upgrade head")
        return False
    
    try:
        # Connect to SQLite database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("✅ Database file exists and is accessible")
        
        # Check what tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print(f"\n📊 Found {len(tables)} tables:")
        for i, (table_name,) in enumerate(tables, 1):
            print(f"  {i}. {table_name}")
        
        # Check if users table exists
        user_table_exists = any(table[0] == 'users' for table in tables)
        
        if not user_table_exists:
            print("\n❌ 'users' table does not exist!")
            print("🔧 This is why the API returns 'User not found'")
            print("\n💻 To fix this:")
            print("1. Run: python3 init_database.py")
            print("2. Or run: alembic upgrade head")
            conn.close()
            return False
        
        print("\n✅ 'users' table exists")
        
        # Check users table schema
        cursor.execute("PRAGMA table_info(users);")
        schema = cursor.fetchall()
        
        print("\n📋 Users table schema:")
        for col in schema:
            col_id, name, col_type, not_null, default, pk = col
            print(f"  - {name}: {col_type} {'(PRIMARY KEY)' if pk else ''}")
        
        # Check users table data
        cursor.execute("SELECT COUNT(*) FROM users;")
        user_count = cursor.fetchone()[0]
        
        print(f"\n👥 Users in database: {user_count}")
        
        if user_count == 0:
            print("⚠️ Users table is empty!")
            print("🔧 This might be why the API can't find users")
            print("\n💻 To fix this:")
            print("1. Create a test user in the database")
            print("2. Run the seed data script")
            print("3. Or modify the API to handle empty user tables")
        else:
            # Show sample users
            cursor.execute("SELECT id, email, full_name, role, is_active FROM users LIMIT 5;")
            users = cursor.fetchall()
            
            print("\n🔍 Sample users:")
            for user in users:
                user_id, email, full_name, role, is_active = user
                print(f"  - ID: {user_id}, Email: {email}, Name: {full_name}, Role: {role}, Active: {is_active}")
        
        conn.close()
        return user_count > 0
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        return False

def main():
    """Main function"""
    success = check_sqlite_database()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ Database has users - API error might be authentication-related")
    else:
        print("❌ Database issue found - this explains the 'User not found' error")
    
    print("\n🔍 Next steps:")
    print("1. Fix database issues if any")
    print("2. Check API authentication logic")
    print("3. Verify user ID extraction from requests")

if __name__ == "__main__":
    main()