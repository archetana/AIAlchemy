#!/bin/bash
# Deploy NGINX Gateway to Cloud Run

set -e

# Configuration
PROJECT_ID="aialchemy-prod"
REGION="us-central1"
GATEWAY_SERVICE="aialchemy-gateway"
BACKEND_SERVICE="aialchemy-backend"
FRONTEND_SERVICE="aialchemy-frontend"

echo "🚀 Deploying NGINX Gateway to Cloud Run..."

# Set project
gcloud config set project $PROJECT_ID

# Get service URLs
BACKEND_URL=$(gcloud run services describe $BACKEND_SERVICE --region=$REGION --format='value(status.url)')
FRONTEND_URL=$(gcloud run services describe $FRONTEND_SERVICE --region=$REGION --format='value(status.url)')

echo "📋 Service URLs:"
echo "  Backend:  $BACKEND_URL"
echo "  Frontend: $FRONTEND_URL"

# Build and deploy gateway
cd gateway

echo "🐳 Building and deploying gateway service..."
gcloud run deploy $GATEWAY_SERVICE \
    --source . \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --memory 256Mi \
    --cpu 1 \
    --timeout 300 \
    --max-instances 10 \
    --port 8080 \
    --set-env-vars "BACKEND_URL=$BACKEND_URL,FRONTEND_URL=$FRONTEND_URL"

# Get gateway URL
GATEWAY_URL=$(gcloud run services describe $GATEWAY_SERVICE --region=$REGION --format='value(status.url)')

echo ""
echo "🎉 NGINX Gateway Deployed Successfully!"
echo "======================================="
echo "Gateway URL: $GATEWAY_URL"
echo ""
echo "🔀 Traffic Routing:"
echo "  $GATEWAY_URL/api/* → Backend API ($BACKEND_URL)"
echo "  $GATEWAY_URL/* → Frontend App ($FRONTEND_URL)"
echo ""
echo "📊 Test endpoints:"
echo "  Frontend: $GATEWAY_URL"
echo "  API Health: $GATEWAY_URL/api/health"
echo "  Gateway Health: $GATEWAY_URL/health"
echo "  API Docs: $GATEWAY_URL/docs"
echo ""
echo "🔄 Update gateway:"
echo "cd gateway && gcloud run deploy $GATEWAY_SERVICE --source ."

cd ..