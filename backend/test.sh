#!/bin/bash

# Comprehensive test runner script
# Usage: ./test.sh [quick|full|category]

set -e  # Exit on any error

echo "🚀 FastAPI Application Test Suite"
echo "================================="

# Change to backend directory
cd "$(dirname "$0")"

# Activate virtual environment if it exists, create if it doesn't
if [ -d "venv" ]; then
    echo "📦 Activating virtual environment..."
    source venv/bin/activate
else
    echo "📦 Creating and setting up virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
fi

# Install/update dependencies
echo "📦 Installing dependencies..."
pip install -q pytest pytest-asyncio pytest-httpx

# Run tests based on argument
case "${1:-full}" in
    "quick")
        echo "⚡ Running quick health checks..."
        python -m pytest tests/test_health.py tests/test_database.py -v
        ;;
    "auth")
        echo "🔐 Running authentication tests..."
        python -m pytest tests/test_auth.py tests/test_password_hashing.py -v
        ;;
    "api")
        echo "🌐 Running API tests..."
        python -m pytest tests/test_api_endpoints.py -v
        ;;
    "full")
        echo "🧪 Running comprehensive test suite..."
        python run_tests.py
        ;;
    *)
        echo "Usage: $0 [quick|auth|api|full]"
        echo "  quick - Health and database connectivity tests"
        echo "  auth  - Authentication system tests" 
        echo "  api   - API endpoint tests"
        echo "  full  - Complete test suite (default)"
        exit 1
        ;;
esac

echo ""
echo "✅ Tests completed successfully!"