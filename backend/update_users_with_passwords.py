#!/usr/bin/env python3
"""
Update existing users with hashed passwords
This is a one-time script to add password fields to existing users
"""

import sqlite3
from app.auth.password_utils import hash_password
from datetime import datetime

def update_existing_users():
    """Add password field to existing users"""
    print("🔐 Adding Password Fields to Existing Users")
    print("=" * 50)
    
    try:
        # Connect to database
        conn = sqlite3.connect("./aialchemy.db")
        cursor = conn.cursor()
        
        # Add the password column if it doesn't exist
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN hashed_password VARCHAR(255)")
            print("✅ Added hashed_password column")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print("ℹ️ hashed_password column already exists")
            else:
                raise
        
        # Add the last_login_at column if it doesn't exist
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN last_login_at DATETIME")
            print("✅ Added last_login_at column")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print("ℹ️ last_login_at column already exists")
            else:
                raise
        
        # Get users without passwords
        cursor.execute("SELECT id, email, full_name FROM users WHERE hashed_password IS NULL")
        users = cursor.fetchall()
        
        if not users:
            print("ℹ️ All users already have passwords")
            conn.close()
            return
        
        print(f"\n👥 Found {len(users)} users without passwords")
        
        # Default password for all existing users
        default_password = "TempPass123!"
        hashed_password = hash_password(default_password)
        
        # Update each user
        for user_id, email, full_name in users:
            cursor.execute(
                "UPDATE users SET hashed_password = ? WHERE id = ?",
                (hashed_password, user_id)
            )
            print(f"   ✅ Updated user: {email} ({full_name})")
        
        conn.commit()
        
        print(f"\n✅ Successfully updated {len(users)} users")
        print("🔑 Default password for all users: TempPass123!")
        print("⚠️  Users should change their passwords after first login")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error updating users: {e}")
        return False

def main():
    """Main function"""
    success = update_existing_users()
    
    if success:
        print("\n" + "=" * 50)
        print("✅ SUCCESS: Users updated with password fields!")
        print("\n📋 User Login Information:")
        print("   Email: test@example.com")
        print("   Password: TempPass123!")
        print("   Role: ADMIN")
        print("\n   Email: admin@aialchemy.com")
        print("   Password: TempPass123!")
        print("   Role: ADMIN")
        
        print("\n🚀 Authentication system is now ready to use!")
    else:
        print("\n❌ Failed to update users")

if __name__ == "__main__":
    main()