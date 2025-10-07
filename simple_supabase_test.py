#!/usr/bin/env python3
"""
Simple Supabase Vector Test
Tests if your vector database setup is working
"""

import os
import sys

def test_supabase_connection():
    """Test basic Supabase connection"""
    
    print("🧪 Testing Supabase Vector Database Setup")
    print("=" * 50)
    
    # Check environment variables
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_ANON_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ Missing Supabase credentials!")
        print("\n💡 To test with your credentials:")
        print("export SUPABASE_URL='https://your-project-id.supabase.co'")
        print("export SUPABASE_ANON_KEY='your-anon-key'")
        print("python3 simple_supabase_test.py")
        return False
    
    try:
        from supabase import create_client, Client
        
        print(f"✅ Supabase URL: {supabase_url[:30]}...")
        print(f"✅ Supabase Key: {supabase_key[:20]}...")
        
        # Create client
        supabase: Client = create_client(supabase_url, supabase_key)
        print("✅ Supabase client created")
        
        # Test basic connection
        result = supabase.table('users').select('count').execute()
        print(f"✅ Connected to database")
        
        # Check if vector tables exist
        vector_tables = ['document_vectors', 'document_chunks', 'search_cache']
        existing_tables = []
        
        for table in vector_tables:
            try:
                result = supabase.table(table).select('count').limit(1).execute()
                existing_tables.append(table)
                print(f"✅ Table '{table}' exists")
            except Exception as e:
                print(f"❌ Table '{table}' missing: {str(e)}")
        
        # Check users table
        try:
            result = supabase.table('users').select('email, username').limit(5).execute()
            user_count = len(result.data) if result.data else 0
            print(f"✅ Users table: {user_count} users found")
            
            if result.data:
                for user in result.data:
                    print(f"   👤 {user.get('username', 'N/A')} ({user.get('email', 'N/A')})")
                    
        except Exception as e:
            print(f"❌ Could not access users table: {e}")
        
        # Summary
        print(f"\n📊 Summary:")
        print(f"   Vector tables ready: {len(existing_tables)}/3")
        print(f"   Users: {user_count}")
        
        if len(existing_tables) == 3:
            print(f"\n🎉 Vector database is ready!")
            print(f"\n📋 Next steps:")
            print(f"   1. Login to your app with admin@aialchemy.com / admin123")
            print(f"   2. Use the new /vector-documents/ API endpoints")
            print(f"   3. Upload documents and test semantic search")
        else:
            print(f"\n⚠️  Run the vector_document_schema.sql in Supabase SQL Editor")
            
        return True
        
    except ImportError:
        print("❌ Supabase client not available")
        print("Install with: pip install supabase")
        return False
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def main():
    """Main test function"""
    success = test_supabase_connection()
    
    if success:
        print(f"\n🚀 Your vector database setup is working!")
        print(f"\n🌐 Available API endpoints (once deployed):")
        print(f"   POST /vector-documents/upload")
        print(f"   POST /vector-documents/search") 
        print(f"   GET /vector-documents/search/similar-companies")
        print(f"   GET /vector-documents/startup/{{id}}")
        print(f"   GET /vector-documents/stats")
        print(f"   GET /vector-documents/health")
    else:
        print(f"\n❌ Setup incomplete. Follow the steps above.")

if __name__ == "__main__":
    main()