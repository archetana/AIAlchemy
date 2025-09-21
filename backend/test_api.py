"""
Simple API test script to validate all endpoints
"""

import asyncio
import httpx
import json

BASE_URL = "http://localhost:8000"

async def test_endpoints():
    """Test all main API endpoints"""
    
    async with httpx.AsyncClient() as client:
        print("🔍 Testing AIAlchemy API endpoints...\n")
        
        # Test 1: Root endpoint
        print("1. Testing root endpoint...")
        try:
            response = await client.get(f"{BASE_URL}/")
            if response.status_code == 200:
                print("   ✅ Root endpoint working")
                data = response.json()
                print(f"   📊 Service: {data['service']}")
            else:
                print(f"   ❌ Root endpoint failed: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Root endpoint error: {e}")
        
        # Test 2: Health endpoint
        print("\n2. Testing health endpoint...")
        try:
            response = await client.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                print("   ✅ Health endpoint working")
            else:
                print(f"   ❌ Health endpoint failed: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Health endpoint error: {e}")
        
        # Test 3: Dashboard overview (simplified)
        print("\n3. Testing dashboard overview...")
        try:
            response = await client.get(f"{BASE_URL}/api/dashboard/overview")
            if response.status_code == 200:
                print("   ✅ Dashboard overview working")
                data = response.json()
                if 'data' in data:
                    stats = data['data']
                    print(f"   📊 Total Applications: {stats.get('total_applications', 'N/A')}")
                    print(f"   📊 AI Processing: {stats.get('ai_processing', 'N/A')}")
                    print(f"   📊 Average Score: {stats.get('average_score', 'N/A')}")
            else:
                print(f"   ❌ Dashboard overview failed: {response.status_code}")
                print(f"   📄 Response: {response.text}")
        except Exception as e:
            print(f"   ❌ Dashboard overview error: {e}")
        
        # Test 4: Pipeline stats
        print("\n4. Testing pipeline stats...")
        try:
            response = await client.get(f"{BASE_URL}/api/pipeline/stats")
            if response.status_code == 200:
                print("   ✅ Pipeline stats working")
                data = response.json()
                if 'data' in data:
                    stats = data['data']
                    print(f"   📊 Stages: {len(stats.get('stages', {}))}")
                    print(f"   📊 Weekly Throughput: {stats.get('weekly_throughput', 'N/A')}")
            else:
                print(f"   ❌ Pipeline stats failed: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Pipeline stats error: {e}")
        
        # Test 5: Startups list (first page)
        print("\n5. Testing startups list...")
        try:
            response = await client.get(f"{BASE_URL}/api/startups/?page=1&page_size=5")
            if response.status_code == 200:
                print("   ✅ Startups list working")
                data = response.json()
                print(f"   📊 Total Startups: {data.get('total', 'N/A')}")
                print(f"   📊 Items on Page: {len(data.get('items', []))}")
                if data.get('items'):
                    first_startup = data['items'][0]
                    print(f"   📊 First Startup: {first_startup.get('company_name', 'N/A')}")
            else:
                print(f"   ❌ Startups list failed: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Startups list error: {e}")
        
        # Test 6: Settings - Investment weights
        print("\n6. Testing investment weights...")
        try:
            response = await client.get(f"{BASE_URL}/api/settings/investment-weights")
            if response.status_code == 200:
                print("   ✅ Investment weights working")
                data = response.json()
                print(f"   📊 Market Size Weight: {data.get('market_size_weight', 'N/A')}%")
                print(f"   📊 Team Experience Weight: {data.get('team_experience_weight', 'N/A')}%")
            else:
                print(f"   ❌ Investment weights failed: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Investment weights error: {e}")
        
        # Test 7: Startup detail
        print("\n7. Testing startup detail...")
        try:
            response = await client.get(f"{BASE_URL}/api/startups/1")
            if response.status_code == 200:
                print("   ✅ Startup detail working")
                data = response.json()
                print(f"   📊 Company: {data.get('company_name', 'N/A')}")
                print(f"   📊 Status: {data.get('status', 'N/A')}")
                print(f"   📊 AI Score: {data.get('ai_score', 'N/A')}")
            else:
                print(f"   ❌ Startup detail failed: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Startup detail error: {e}")
        
        print("\n🎉 API testing completed!")

if __name__ == "__main__":
    asyncio.run(test_endpoints())