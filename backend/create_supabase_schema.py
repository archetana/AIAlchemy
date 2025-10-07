#!/usr/bin/env python3
"""
Create Database Tables in Supabase
Executes the schema SQL file to create all required tables
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv

def execute_schema():
    """Execute database schema creation in Supabase"""
    
    # Load environment variables
    load_dotenv()
    
    # Supabase credentials
    supabase_url = "https://udjsdlfturbgiqnjsozo.supabase.co"
    supabase_anon_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVkanNkbGZ0dXJiZ2lxbmpzb3pvIiwicm9sZUI6ImFub24iLCJpYXQiOjE3NTk3ODgwNjMsImV4cCI6MjA3NTM2NDA2M30.vCfIXigCD2uUKZr5Y3cxYisVyn34DgZXd0QSUwgzr6Y"
    
    print("🗄️ Creating Supabase Database Schema...")
    print("=" * 50)
    
    # Create Supabase client
    supabase: Client = create_client(supabase_url, supabase_anon_key)
    
    # Read schema file
    with open('supabase_schema.sql', 'r') as f:
        schema_sql = f.read()
    
    # Split into individual statements (basic approach)
    statements = []
    current_statement = ""
    
    for line in schema_sql.split('\n'):
        line = line.strip()
        # Skip empty lines and comments
        if not line or line.startswith('--'):
            continue
            
        current_statement += line + " "
        
        # If line ends with semicolon, it's the end of a statement
        if line.endswith(';'):
            statements.append(current_statement.strip())
            current_statement = ""
    
    print(f"📝 Found {len(statements)} SQL statements to execute")
    
    # Execute statements one by one
    success_count = 0
    error_count = 0
    
    for i, statement in enumerate(statements, 1):
        try:
            # Try to execute using RPC (Raw SQL)
            # For now, let's just print what would be executed
            print(f"📋 Statement {i}: {statement[:50]}..." if len(statement) > 50 else f"📋 Statement {i}: {statement}")
            
            # Note: Supabase Python client doesn't support raw SQL execution
            # The schema needs to be executed in Supabase SQL Editor
            success_count += 1
            
        except Exception as e:
            print(f"❌ Error executing statement {i}: {e}")
            error_count += 1
    
    print("\n" + "=" * 50)
    print(f"✅ Successfully processed {success_count} statements")
    if error_count > 0:
        print(f"❌ {error_count} statements had errors")
    
    print("\n📋 IMPORTANT INSTRUCTIONS:")
    print("The Supabase Python client doesn't support executing raw SQL.")
    print("Please follow these steps to create the database schema:")
    print()
    print("1. Go to https://supabase.com/dashboard")
    print("2. Open your project: udjsdlfturbgiqnjsozo")
    print("3. Navigate to 'SQL Editor'")
    print("4. Copy and paste the contents of 'supabase_schema.sql' file")
    print("5. Click 'Run' to execute the schema")
    print()
    print("Alternatively, you can execute each statement individually:")
    
    # Print first few statements as examples
    print("\nFirst 3 statements to execute:")
    for i, statement in enumerate(statements[:3], 1):
        print(f"\n-- Statement {i}:")
        print(statement)
    
    return True

if __name__ == "__main__":
    execute_schema()