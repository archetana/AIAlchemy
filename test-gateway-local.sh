#!/bin/bash
# Local test for NGINX gateway configuration

set -e

echo "🧪 Testing NGINX Gateway Configuration Locally..."

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. This test requires Docker."
    exit 1
fi

cd gateway

# Mock service URLs for testing
export BACKEND_URL="httpbin.org"
export FRONTEND_URL="httpbin.org"

echo "🐳 Building NGINX gateway image..."
docker build -t aialchemy-gateway-test .

echo "🚀 Running gateway container on port 8080..."
docker run -d \
    --name aialchemy-gateway-test \
    -p 8080:8080 \
    -e BACKEND_URL=$BACKEND_URL \
    -e FRONTEND_URL=$FRONTEND_URL \
    aialchemy-gateway-test

# Wait for container to start
sleep 5

echo "🔍 Testing gateway endpoints..."

# Test health check
echo "Testing health endpoint..."
if curl -s -f http://localhost:8080/health > /dev/null; then
    echo "✅ Health check passed"
else
    echo "❌ Health check failed"
fi

# Test that nginx is running
echo "Testing NGINX response..."
if curl -s -I http://localhost:8080/health | grep -q "nginx"; then
    echo "✅ NGINX is running"
else
    echo "❌ NGINX response not detected"
fi

echo "🧹 Cleaning up..."
docker stop aialchemy-gateway-test || true
docker rm aialchemy-gateway-test || true
docker rmi aialchemy-gateway-test || true

echo "✅ Local gateway test completed!"
echo ""
echo "📋 To deploy to Cloud Run:"
echo "  ./deploy-nginx-gateway.sh"
echo ""
echo "📋 To deploy with load balancer:"
echo "  DOMAIN_NAME=yourdomain.com ./load-balancer-setup.sh"

cd ..