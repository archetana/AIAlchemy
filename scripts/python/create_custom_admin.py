#!/usr/bin/env python3
"""
AIAlchemy - Create Custom Admin User
This script creates a custom admin user with your preferred credentials
"""

import bcrypt
import sys

def hash_password(password: str) -> str:
    """Generate bcrypt hash for password"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def main():
    print("AIAlchemy - Create Custom Admin User")
    print("="*40)
    
    # Get user input
    email = input("Admin Email: ").strip()
    username = input("Admin Username: ").strip()
    full_name = input("Admin Full Name: ").strip()
    password = input("Admin Password: ").strip()
    
    if not all([email, username, full_name, password]):
        print("❌ All fields are required!")
        sys.exit(1)
    
    # Generate password hash
    print("\n🔐 Generating password hash...")
    password_hash = hash_password(password)
    
    # Generate SQL
    sql = f"""-- Custom Admin User Creation
-- Execute this in Supabase SQL Editor

INSERT INTO users (email, username, full_name, hashed_password, is_active, is_superuser) VALUES
('{email}', '{username}', '{full_name}', '{password_hash}', true, true)
ON CONFLICT (email) DO UPDATE SET
    username = EXCLUDED.username,
    full_name = EXCLUDED.full_name,
    hashed_password = EXCLUDED.hashed_password,
    is_active = true,
    is_superuser = true,
    updated_at = NOW();

-- Verify user creation
SELECT email, username, full_name, is_active, is_superuser, created_at 
FROM users 
WHERE email = '{email}';"""
    
    # Save SQL file
    filename = f"custom_admin_{username}.sql"
    with open(filename, 'w') as f:
        f.write(sql)
    
    print(f"\n✅ SQL script generated: {filename}")
    print(f"\n📋 Admin User Details:")
    print(f"   Email: {email}")
    print(f"   Username: {username}")
    print(f"   Full Name: {full_name}")
    print(f"   Password: {password}")
    print(f"   Hash: {password_hash}")
    print(f"\n🔧 Next Steps:")
    print(f"   1. Copy the SQL from {filename}")
    print(f"   2. Execute in Supabase SQL Editor")
    print(f"   3. Login with: {email} / {password}")

if __name__ == "__main__":
    main()