#!/bin/bash
# AIAlchemy Gateway Setup - Cloud Load Balancer
# This creates a global load balancer that routes traffic to frontend and backend services

set -e

# Configuration
PROJECT_ID="aialchemy-prod"
REGION="us-central1"
BACKEND_SERVICE="aialchemy-backend"
FRONTEND_SERVICE="aialchemy-frontend"
GATEWAY_NAME="aialchemy-gateway"
DOMAIN_NAME="${DOMAIN_NAME:-aialchemy.example.com}"  # Override with your domain

echo "🌐 Setting up Cloud Load Balancer Gateway for AIAlchemy..."

# Set project
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "🔧 Enabling required APIs..."
gcloud services enable compute.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable certificatemanager.googleapis.com

# Get service URLs
BACKEND_URL=$(gcloud run services describe $BACKEND_SERVICE --region=$REGION --format='value(status.url)' | sed 's|https://||')
FRONTEND_URL=$(gcloud run services describe $FRONTEND_SERVICE --region=$REGION --format='value(status.url)' | sed 's|https://||')

echo "📋 Service URLs:"
echo "  Backend:  $BACKEND_URL"
echo "  Frontend: $FRONTEND_URL"

# Create Network Endpoint Groups (NEGs) for Cloud Run services
echo "🔗 Creating Network Endpoint Groups..."

# Backend NEG
gcloud compute network-endpoint-groups create ${GATEWAY_NAME}-backend-neg \
    --region=$REGION \
    --network-endpoint-type=serverless \
    --cloud-run-service=$BACKEND_SERVICE || echo "Backend NEG already exists"

# Frontend NEG  
gcloud compute network-endpoint-groups create ${GATEWAY_NAME}-frontend-neg \
    --region=$REGION \
    --network-endpoint-type=serverless \
    --cloud-run-service=$FRONTEND_SERVICE || echo "Frontend NEG already exists"

# Create Backend Services
echo "🔧 Creating backend services..."

# API Backend Service
gcloud compute backend-services create ${GATEWAY_NAME}-api-backend \
    --global \
    --protocol=HTTPS \
    --enable-cdn \
    --cache-mode=USE_ORIGIN_HEADERS || echo "API backend service already exists"

gcloud compute backend-services add-backend ${GATEWAY_NAME}-api-backend \
    --global \
    --network-endpoint-group=${GATEWAY_NAME}-backend-neg \
    --network-endpoint-group-region=$REGION || echo "Backend already added"

# Frontend Backend Service
gcloud compute backend-services create ${GATEWAY_NAME}-frontend-backend \
    --global \
    --protocol=HTTPS \
    --enable-cdn \
    --cache-mode=CACHE_ALL_STATIC || echo "Frontend backend service already exists"

gcloud compute backend-services add-backend ${GATEWAY_NAME}-frontend-backend \
    --global \
    --network-endpoint-group=${GATEWAY_NAME}-frontend-neg \
    --network-endpoint-group-region=$REGION || echo "Frontend already added"

# Create URL Map for routing
echo "🗺️ Creating URL map for traffic routing..."
cat > /tmp/url-map.yaml << EOF
name: ${GATEWAY_NAME}-url-map
defaultService: projects/$PROJECT_ID/global/backendServices/${GATEWAY_NAME}-frontend-backend
hostRules:
- hosts:
  - '$DOMAIN_NAME'
  pathMatcher: aialchemy-matcher
pathMatchers:
- name: aialchemy-matcher
  defaultService: projects/$PROJECT_ID/global/backendServices/${GATEWAY_NAME}-frontend-backend
  pathRules:
  - paths:
    - /api/*
    - /docs*
    - /redoc*
    - /openapi.json
    service: projects/$PROJECT_ID/global/backendServices/${GATEWAY_NAME}-api-backend
  - paths:
    - /*
    service: projects/$PROJECT_ID/global/backendServices/${GATEWAY_NAME}-frontend-backend
EOF

gcloud compute url-maps import ${GATEWAY_NAME}-url-map \
    --source=/tmp/url-map.yaml \
    --global || echo "URL map already exists, updating..."

# Create SSL certificate (managed)
echo "🔒 Creating SSL certificate..."
gcloud compute ssl-certificates create ${GATEWAY_NAME}-ssl-cert \
    --domains=$DOMAIN_NAME \
    --global || echo "SSL certificate already exists"

# Create HTTPS proxy
echo "🔐 Creating HTTPS proxy..."
gcloud compute target-https-proxies create ${GATEWAY_NAME}-https-proxy \
    --ssl-certificates=${GATEWAY_NAME}-ssl-cert \
    --url-map=${GATEWAY_NAME}-url-map || echo "HTTPS proxy already exists"

# Create global forwarding rule
echo "🌍 Creating global forwarding rule..."
gcloud compute forwarding-rules create ${GATEWAY_NAME}-https-rule \
    --global \
    --target-https-proxy=${GATEWAY_NAME}-https-proxy \
    --ports=443 || echo "Forwarding rule already exists"

# Get the external IP
EXTERNAL_IP=$(gcloud compute forwarding-rules describe ${GATEWAY_NAME}-https-rule --global --format='value(IPAddress)')

echo ""
echo "🎉 Gateway Setup Complete!"
echo "=========================="
echo "External IP: $EXTERNAL_IP"
echo "Domain: https://$DOMAIN_NAME"
echo ""
echo "📋 DNS Configuration Required:"
echo "Create an A record for '$DOMAIN_NAME' pointing to $EXTERNAL_IP"
echo ""
echo "🔀 Traffic Routing:"
echo "  /$DOMAIN_NAME/api/* → Backend API"
echo "  /$DOMAIN_NAME/* → Frontend App"
echo ""
echo "📊 Monitor:"
echo "gcloud compute url-maps list"
echo "gcloud compute ssl-certificates list"
echo ""
echo "🔄 Update routing:"
echo "Edit /tmp/url-map.yaml and run:"
echo "gcloud compute url-maps import ${GATEWAY_NAME}-url-map --source=/tmp/url-map.yaml --global"

# Cleanup
rm -f /tmp/url-map.yaml