#!/bin/bash

# Quick Test Runner - Fast validation before committing
# This script runs essential tests quickly to catch major issues

set -e

echo "⚡ AI Alchemy - Quick Test Suite"
echo "================================"
echo "Running essential tests to verify application health..."

# Change to the project root
cd "$(dirname "$0")"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Function to run a test and track results
run_test() {
    local test_name="$1"
    local test_command="$2"
    local test_dir="${3:-.}"
    
    echo -e "\n🧪 Testing: $test_name"
    echo "----------------------------------------"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    if (cd "$test_dir" && eval "$test_command") > /dev/null 2>&1; then
        echo -e "   ${GREEN}✅ PASS${NC} - $test_name"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        return 0
    else
        echo -e "   ${RED}❌ FAIL${NC} - $test_name"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return 1
    fi
}

# Function to show test details on failure
run_test_verbose() {
    local test_name="$1"
    local test_command="$2"
    local test_dir="${3:-.}"
    
    echo -e "\n🧪 Testing: $test_name"
    echo "----------------------------------------"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    if (cd "$test_dir" && eval "$test_command"); then
        echo -e "   ${GREEN}✅ PASS${NC} - $test_name"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        return 0
    else
        echo -e "   ${RED}❌ FAIL${NC} - $test_name"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return 1
    fi
}

echo "📋 Running Quick Health Checks..."

# 1. Backend Health Tests
run_test "Backend Dependencies" "source venv/bin/activate && python -c 'import fastapi, sqlalchemy, uvicorn, pytest'" "backend"
run_test "Backend Syntax Check" "source venv/bin/activate && python -m py_compile app/main.py" "backend"
run_test "Backend Database Test" "source venv/bin/activate && python -m pytest tests/test_simple.py -v --tb=short" "backend"

# 2. Frontend Health Tests  
if command -v npm &> /dev/null; then
    run_test "Frontend Dependencies" "npm ls --depth=0" "frontend"
    run_test "Frontend Build Check" "npm run build" "frontend"
else
    echo -e "\n   ${YELLOW}⏭️  SKIP${NC} - Frontend tests (npm not available in sandbox)"
    echo "   This is expected in headless environments"
fi

# 3. Critical Backend API Tests
echo -e "\n📡 Testing Critical Backend APIs..."
run_test_verbose "Basic Framework Test" "source venv/bin/activate && python -m pytest tests/test_simple.py -v --tb=short" "backend"

# 4. Basic Integration Test
echo -e "\n🔗 Basic Integration Test..."
if command -v curl &> /dev/null; then
    # Try to start backend briefly for health check
    (cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8002 &) 
    BACKEND_PID=$!
    
    sleep 5
    
    if run_test "Backend Health Endpoint" "curl -f http://localhost:8002/health"; then
        echo "   Backend is responding correctly"
    else
        echo "   Backend health check failed"
    fi
    
    # Clean up
    kill $BACKEND_PID 2>/dev/null || true
    wait $BACKEND_PID 2>/dev/null || true
else
    echo "   ⏭️  Skipping integration test (curl not available)"
fi

# Report Results
echo ""
echo "================================"
echo "📊 Quick Test Results Summary"
echo "================================"
echo -e "Total Tests: $TOTAL_TESTS"
echo -e "${GREEN}✅ Passed: $PASSED_TESTS${NC}"
echo -e "${RED}❌ Failed: $FAILED_TESTS${NC}"

SUCCESS_RATE=$(( PASSED_TESTS * 100 / TOTAL_TESTS ))
echo -e "Success Rate: $SUCCESS_RATE%"

echo ""
if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}🎉 ALL QUICK TESTS PASSED!${NC}"
    echo "✅ Application appears healthy"
    echo "✅ Safe to proceed with full testing or deployment"
    echo ""
    echo "💡 To run comprehensive tests: ./run_all_tests.py"
    exit 0
else
    echo -e "${RED}⚠️  $FAILED_TESTS TESTS FAILED${NC}"
    echo "❌ Issues detected that need attention"
    echo "❌ Fix these issues before deployment"
    echo ""
    echo "🔧 Run individual test suites for details:"
    echo "   Backend: cd backend && ./test.sh"
    echo "   Frontend: cd frontend && npm test"
    echo "   Full Suite: ./run_all_tests.py"
    exit 1
fi