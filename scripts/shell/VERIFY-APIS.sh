#!/bin/bash

echo "🔍 AIAlchemy API Verification Script"
echo "=================================="
echo ""

BASE_URL="http://localhost:8000"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to test endpoint
test_endpoint() {
    local name="$1"
    local url="$2"
    local method="${3:-GET}"
    
    printf "%-40s" "$name:"
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "%{http_code}" "$url")
        http_code="${response: -3}"
        body="${response%???}"
    else
        http_code=$(curl -s -w "%{http_code}" -X "$method" "$url" -o /dev/null)
    fi
    
    if [ "$http_code" = "200" ]; then
        echo -e "${GREEN}✅ OK${NC} (200)"
        if [ ${#body} -gt 0 ] && [ ${#body} -lt 200 ]; then
            echo "    Response: $body"
        elif [ ${#body} -gt 200 ]; then
            echo "    Response: ${body:0:100}..."
        fi
    else
        echo -e "${RED}❌ FAIL${NC} ($http_code)"
    fi
    echo ""
}

echo "🏠 SYSTEM ENDPOINTS"
echo "-------------------"
test_endpoint "Health Check" "$BASE_URL/health"
test_endpoint "API Status" "$BASE_URL/api/status"
test_endpoint "Service Info" "$BASE_URL/"

echo ""
echo "📊 DASHBOARD API"
echo "----------------"
test_endpoint "Dashboard Overview" "$BASE_URL/api/dashboard/overview"
test_endpoint "Dashboard Stats" "$BASE_URL/api/dashboard/stats"

echo ""
echo "🚀 STARTUPS API" 
echo "---------------"
test_endpoint "Startups List (Page 1)" "$BASE_URL/api/startups/?page=1&page_size=3"
test_endpoint "Startup Detail (ID=1)" "$BASE_URL/api/startups/1"
test_endpoint "Filter by Status" "$BASE_URL/api/startups/?status=ai_analysis"
test_endpoint "Search Companies" "$BASE_URL/api/startups/search/suggestions?query=Tech"
test_endpoint "Status Count" "$BASE_URL/api/startups/status/new/count"

echo ""
echo "🏭 PIPELINE API"
echo "---------------"
test_endpoint "Pipeline Stats" "$BASE_URL/api/pipeline/stats"
test_endpoint "Pipeline Stages" "$BASE_URL/api/pipeline/stages"
test_endpoint "Bottlenecks Analysis" "$BASE_URL/api/pipeline/bottlenecks"
test_endpoint "Throughput Metrics" "$BASE_URL/api/pipeline/throughput?days=30"

echo ""
echo "📝 INVESTMENT MEMOS API"
echo "------------------------"
test_endpoint "Memo for Startup 1" "$BASE_URL/api/memos/startup/1"
test_endpoint "All Memos List" "$BASE_URL/api/memos/?page_size=5"
test_endpoint "Memo Statistics" "$BASE_URL/api/memos/stats/summary"

echo ""
echo "📁 FILE UPLOADS API"
echo "-------------------"
test_endpoint "Startup 1 Files" "$BASE_URL/api/uploads/startup/1/files"
test_endpoint "Upload Statistics" "$BASE_URL/api/uploads/stats/summary"

echo ""
echo "⚙️ SETTINGS API"
echo "---------------"
test_endpoint "Current User Profile" "$BASE_URL/api/settings/users/me"
test_endpoint "All Users List" "$BASE_URL/api/settings/users"
test_endpoint "Industries List" "$BASE_URL/api/settings/industries"
test_endpoint "Investment Weights" "$BASE_URL/api/settings/investment-weights"
test_endpoint "Account Preferences" "$BASE_URL/api/settings/account/preferences"
test_endpoint "System Information" "$BASE_URL/api/settings/system/info"

echo ""
echo "🎯 QUICK SAMPLE DATA VERIFICATION"
echo "===================================="

echo -e "${BLUE}📊 Dashboard Overview:${NC}"
curl -s "$BASE_URL/api/dashboard/overview" | head -c 300
echo ""
echo ""

echo -e "${BLUE}🏢 First 2 Startups:${NC}"
curl -s "$BASE_URL/api/startups/?page_size=2" | head -c 400  
echo ""
echo ""

echo -e "${BLUE}📈 Pipeline Summary:${NC}"
curl -s "$BASE_URL/api/pipeline/stats" | head -c 300
echo ""
echo ""

echo -e "${BLUE}⚖️ Investment Weights:${NC}"
curl -s "$BASE_URL/api/settings/investment-weights" | head -c 200
echo ""
echo ""

echo "🎉 API Verification Complete!"
echo ""
echo -e "${YELLOW}📚 Full API Documentation: http://localhost:8000/docs${NC}"
echo -e "${YELLOW}🔍 Interactive API Explorer: http://localhost:8000/docs#/${NC}"
echo ""
echo "ℹ️  All endpoints tested. Check individual responses above for detailed data."
echo "ℹ️  Server logs available at: /tmp/aialchemy.log"