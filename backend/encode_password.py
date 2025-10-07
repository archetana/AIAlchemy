#!/usr/bin/env python3
"""
Database Password URL Encoder
Helps encode passwords with special characters for database URLs
"""

import urllib.parse
import sys

def encode_password(password):
    """URL encode a password for use in database URLs"""
    return urllib.parse.quote_plus(password)

def build_database_url(project_id, password, db_name="postgres"):
    """Build a complete Supabase database URL with encoded password"""
    encoded_password = encode_password(password)
    return f"postgresql+asyncpg://postgres:{encoded_password}@db.{project_id}.supabase.co:5432/{db_name}"

def main():
    if len(sys.argv) < 2:
        print("Password URL Encoder for Database Connections")
        print("Usage:")
        print("  python encode_password.py 'your_password'")
        print("  python encode_password.py 'your_password' 'project_id'")
        print("")
        print("Examples:")
        print("  python encode_password.py 'AIARC@123'")
        print("  python encode_password.py 'my_pass!word#123' 'udjsdlfturbgiqnjsozo'")
        return
    
    password = sys.argv[1]
    encoded = encode_password(password)
    
    print(f"Original password: {password}")
    print(f"URL encoded:       {encoded}")
    
    if len(sys.argv) >= 3:
        project_id = sys.argv[2]
        database_url = build_database_url(project_id, password)
        print(f"Complete URL:      {database_url}")
        print("")
        print("Add this to your .env file:")
        print(f"DATABASE_URL={database_url}")

if __name__ == "__main__":
    main()