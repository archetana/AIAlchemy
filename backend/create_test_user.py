#!/usr/bin/env python3
"""
Create a test user for AIAlchemy
"""

import sqlite3
from datetime import datetime

def create_test_user():
    """Create a test user in the database"""
    print("👤 Creating Test User")
    print("=" * 30)
    
    try:
        # Connect to SQLite database
        conn = sqlite3.connect("./aialchemy.db")
        cursor = conn.cursor()
        
        # Check if user already exists
        cursor.execute("SELECT COUNT(*) FROM users WHERE email = ?", ("test@example.com",))
        exists = cursor.fetchone()[0]
        
        if exists > 0:
            print("ℹ️ Test user already exists")
            cursor.execute("SELECT id, email, full_name, role FROM users WHERE email = ?", ("test@example.com",))
            user = cursor.fetchone()
            print(f"   ID: {user[0]}, Email: {user[1]}, Name: {user[2]}, Role: {user[3]}")
            conn.close()
            return True
        
        # Create test user
        now = datetime.now().isoformat()
        
        cursor.execute("""
            INSERT INTO users (
                email, full_name, title, role, is_active, created_at
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            "test@example.com",
            "Test User",
            "Developer",
            "ADMIN",
            1,  # True for is_active
            now
        ))
        
        user_id = cursor.lastrowid
        conn.commit()
        
        print(f"✅ Test user created successfully!")
        print(f"   ID: {user_id}")
        print(f"   Email: test@example.com")
        print(f"   Name: Test User")
        print(f"   Role: ADMIN")
        print(f"   Active: True")
        
        # Create a few more sample users
        sample_users = [
            ("admin@aialchemy.com", "Admin User", "Platform Administrator", "ADMIN"),
            ("analyst@aialchemy.com", "Jane Analyst", "Investment Analyst", "ANALYST"),
            ("partner@aialchemy.com", "John Partner", "Investment Partner", "PARTNER"),
        ]
        
        for email, name, title, role in sample_users:
            cursor.execute("""
                INSERT INTO users (
                    email, full_name, title, role, is_active, created_at
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (email, name, title, role, 1, now))
        
        conn.commit()
        
        # Show all users
        cursor.execute("SELECT id, email, full_name, role, is_active FROM users")
        users = cursor.fetchall()
        
        print(f"\n📊 Total users created: {len(users)}")
        print("\n👥 All users in database:")
        for user in users:
            user_id, email, full_name, role, is_active = user
            status = "✅ Active" if is_active else "❌ Inactive"
            print(f"   ID: {user_id} | {email} | {full_name} | {role} | {status}")
        
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        return False

def main():
    """Main function"""
    success = create_test_user()
    
    if success:
        print("\n" + "=" * 50)
        print("✅ SUCCESS: Test users created!")
        print("🔧 The 'User not found' error should now be resolved")
        print("\n🔍 Next steps:")
        print("1. Test the API endpoint again")
        print("2. Ensure your API authentication uses one of these user IDs")
        print("3. Or implement proper user login/registration")
        
        print("\n💡 API Testing:")
        print("   Try accessing the preferences endpoint with user ID 1-4")
        print("   The API should now find these users in the database")
    else:
        print("\n❌ Failed to create test users")

if __name__ == "__main__":
    main()