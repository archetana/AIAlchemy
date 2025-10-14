#!/usr/bin/env python3
"""
Test Vector Database Setup
Verifies that your vector database is working correctly
"""

import asyncio
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent / "backend"))

from app.services.vector_document_service import vector_document_service

async def test_vector_database():
    """Test vector database functionality"""
    
    print("🧪 Testing Vector Database Setup")
    print("=" * 50)
    
    # Test 1: Basic embedding generation
    print("1. Testing embedding generation...")
    try:
        test_text = "This is a test document about AI and machine learning"
        embedding = await vector_document_service.generate_embedding(test_text)
        
        if embedding and len(embedding) > 0:
            print(f"   ✅ Embedding generated: {len(embedding)} dimensions")
            if len(embedding) != 1536:
                print(f"   ⚠️  Using fallback embedding (expected: 1536, got: {len(embedding)})")
            else:
                print(f"   🎉 Using OpenAI embeddings!")
        else:
            print("   ❌ Failed to generate embedding")
            return False
    except Exception as e:
        print(f"   ❌ Embedding error: {e}")
        return False
    
    # Test 2: Database connection
    print("\n2. Testing Supabase connection...")
    try:
        # Test basic query
        result = vector_document_service.supabase.table('users').select('count').execute()
        print(f"   ✅ Supabase connected successfully")
        print(f"   📊 Found {len(result.data) if result.data else 0} users")
    except Exception as e:
        print(f"   ❌ Supabase connection error: {e}")
        return False
    
    # Test 3: Vector table exists
    print("\n3. Testing vector tables...")
    try:
        # Check if vector tables exist
        tables_to_check = ['document_vectors', 'document_chunks', 'search_cache']
        for table in tables_to_check:
            result = vector_document_service.supabase.table(table).select('count').execute()
            print(f"   ✅ Table '{table}' exists")
    except Exception as e:
        print(f"   ❌ Vector tables error: {e}")
        return False
    
    # Test 4: Store sample document
    print("\n4. Testing document storage...")
    try:
        # Store a test document
        sample_startup_id = 1  # Assuming we have at least one startup
        
        document_id = await vector_document_service.store_document_vector(
            startup_id=sample_startup_id,
            document_type="test_document",
            filename="test_pitch_deck.pdf",
            raw_text="This is a test pitch deck about an AI startup that builds machine learning solutions for healthcare.",
            structured_data={
                "company_name": "Test AI Startup",
                "industry": "AI/Healthcare",
                "funding_request": "$2M"
            },
            extraction_service="test_service",
            extraction_confidence=95.0,
            content_categories=["ai", "healthcare"],
            key_entities={"companies": ["Test AI Startup"], "technologies": ["AI", "ML"]}
        )
        
        print(f"   ✅ Document stored with ID: {document_id}")
        
    except Exception as e:
        print(f"   ❌ Document storage error: {e}")
        return False
    
    # Test 5: Semantic search
    print("\n5. Testing semantic search...")
    try:
        search_results = await vector_document_service.semantic_search(
            query_text="artificial intelligence healthcare",
            similarity_threshold=0.3,  # Lower threshold for test
            max_results=5
        )
        
        print(f"   ✅ Search completed: {len(search_results)} results")
        for i, result in enumerate(search_results[:2]):  # Show first 2 results
            print(f"   📄 Result {i+1}: {result.get('filename', 'N/A')} (score: {result.get('similarity_score', 'N/A')})")
            
    except Exception as e:
        print(f"   ❌ Search error: {e}")
        return False
    
    # Test 6: Document stats
    print("\n6. Testing analytics...")
    try:
        stats = await vector_document_service.get_document_stats()
        if stats.get('success'):
            print(f"   ✅ Analytics working: {stats.get('total_startups', 0)} startups with documents")
        else:
            print(f"   ⚠️  Analytics issue: {stats.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"   ❌ Analytics error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Vector Database Test Complete!")
    print("\n📋 Next Steps:")
    print("1. Deploy your updated app to production")
    print("2. Login with admin@aialchemy.com / admin123")
    print("3. Upload real documents via the API")
    print("4. Try semantic search queries")
    print("\n💡 API Endpoints available:")
    print("- POST /vector-documents/upload")
    print("- POST /vector-documents/search")
    print("- GET /vector-documents/search/similar-companies")
    print("- GET /vector-documents/stats")
    
    return True

async def test_api_endpoints():
    """Test API endpoint availability"""
    print("\n🌐 Testing API Endpoints...")
    
    try:
        import requests
        
        # Get your app URL (you'll need to update this)
        base_url = "https://your-app.run.app"  # Update with your actual URL
        
        # Test health endpoint
        try:
            response = requests.get(f"{base_url}/vector-documents/health", timeout=5)
            if response.status_code == 200:
                print(f"   ✅ Vector API health check passed")
                data = response.json()
                print(f"   📊 Status: {data.get('status', 'unknown')}")
            else:
                print(f"   ⚠️  API returned status {response.status_code}")
        except requests.exceptions.RequestException:
            print(f"   ⚠️  Could not reach API (expected if not deployed yet)")
            
    except ImportError:
        print("   ⚠️  requests library not available, skipping API test")

def main():
    """Run all tests"""
    print("🚀 AIAlchemy Vector Database Setup Test")
    print("=" * 60)
    
    # Check environment
    print("🔧 Environment Check:")
    supabase_url = os.getenv('SUPABASE_URL', 'Not set')
    supabase_key = os.getenv('SUPABASE_ANON_KEY', 'Not set')
    openai_key = os.getenv('OPENAI_API_KEY', 'Not set')
    
    print(f"   SUPABASE_URL: {'✅ Set' if supabase_url != 'Not set' else '❌ Not set'}")
    print(f"   SUPABASE_ANON_KEY: {'✅ Set' if supabase_key != 'Not set' else '❌ Not set'}")
    print(f"   OPENAI_API_KEY: {'✅ Set' if openai_key != 'Not set' else '⚠️  Not set (will use fallback)'}")
    
    if supabase_url == 'Not set' or supabase_key == 'Not set':
        print("\n❌ Missing Supabase credentials!")
        print("Set environment variables:")
        print("export SUPABASE_URL='your-supabase-url'")
        print("export SUPABASE_ANON_KEY='your-supabase-anon-key'")
        return
    
    print("\n" + "=" * 60)
    
    # Run async tests
    try:
        success = asyncio.run(test_vector_database())
        if success:
            asyncio.run(test_api_endpoints())
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()