#!/usr/bin/env python3
"""
Execute Schema Directly in Supabase PostgreSQL
Uses psycopg2 to connect directly to the database and execute the schema
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os

def execute_schema_direct():
    """Execute database schema creation directly in PostgreSQL"""
    
    print("🗄️ Executing Database Schema in Supabase PostgreSQL...")
    print("=" * 60)
    
    # Database connection parameters
    connection_params = {
        'host': 'db.udjsdlfturbgiqnjsozo.supabase.co',
        'port': 5432,
        'database': 'postgres',
        'user': 'postgres',
        'password': 'AIARC@123'
    }
    
    try:
        # Connect to database
        print("🔗 Connecting to Supabase PostgreSQL...")
        conn = psycopg2.connect(**connection_params)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        print("✅ Connected successfully!")
        
        # Read schema file
        print("📖 Reading schema file...")
        with open('supabase_schema.sql', 'r') as f:
            schema_sql = f.read()
        
        # Execute the entire schema
        print("🚀 Executing schema SQL...")
        cursor.execute(schema_sql)
        
        print("✅ Schema executed successfully!")
        
        # Test if tables were created
        print("\n🔍 Verifying table creation...")
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """)
        
        tables = cursor.fetchall()
        print(f"📋 Found {len(tables)} tables:")
        for table in tables:
            print(f"  ✓ {table[0]}")
        
        # Test enums
        print("\n🔍 Verifying enum types...")
        cursor.execute("""
            SELECT typname 
            FROM pg_type 
            WHERE typtype = 'e'
            ORDER BY typname;
        """)
        
        enums = cursor.fetchall()
        print(f"📋 Found {len(enums)} enum types:")
        for enum in enums:
            print(f"  ✓ {enum[0]}")
        
        cursor.close()
        conn.close()
        
        print("\n🎉 Database schema creation completed successfully!")
        return True
        
    except psycopg2.Error as e:
        print(f"❌ PostgreSQL error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = execute_schema_direct()
    if success:
        print("\n✅ All done! You can now test the Supabase integration.")
    else:
        print("\n❌ Schema creation failed. Please check the errors above.")