#!/bin/bash
# AIAlchemy Google Cloud Load Balancer Setup Script
# Automated setup of load balancer for frontend and backend services

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID="${PROJECT_ID:-aialchemy-prod}"
REGION="${REGION:-us-central1}"
DOMAIN_NAME="${DOMAIN_NAME:-}"

# Function to print colored output
print_status() {
    echo -e "${BLUE}🔧 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Function to check if resource exists
resource_exists() {
    local resource_type="$1"
    local resource_name="$2"
    local additional_flags="$3"
    
    if gcloud compute $resource_type describe $resource_name $additional_flags &>/dev/null; then
        return 0
    else
        return 1
    fi
}

echo "🌐 AIAlchemy Google Cloud Load Balancer Setup"
echo "============================================="

# Validate inputs
if [ -z "$DOMAIN_NAME" ]; then
    print_error "DOMAIN_NAME environment variable is required"
    echo "Usage: DOMAIN_NAME=yourdomain.com PROJECT_ID=your-project ./setup-load-balancer.sh"
    exit 1
fi

print_status "Using configuration:"
echo "  Project ID: $PROJECT_ID"
echo "  Region: $REGION"
echo "  Domain: $DOMAIN_NAME"
echo ""

# Set project
print_status "Setting GCP project to $PROJECT_ID"
gcloud config set project $PROJECT_ID

# Enable APIs
print_status "Enabling required APIs"
gcloud services enable compute.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable certificatemanager.googleapis.com
print_success "APIs enabled"

# Verify services exist
print_status "Verifying Cloud Run services exist"
BACKEND_URL=$(gcloud run services describe aialchemy-backend --region=$REGION --format='value(status.url)' 2>/dev/null || echo "")
FRONTEND_URL=$(gcloud run services describe aialchemy-frontend --region=$REGION --format='value(status.url)' 2>/dev/null || echo "")

if [ -z "$BACKEND_URL" ] || [ -z "$FRONTEND_URL" ]; then
    print_error "Backend and frontend services must be deployed first"
    echo "Backend URL: $BACKEND_URL"
    echo "Frontend URL: $FRONTEND_URL"
    echo ""
    echo "Deploy services first:"
    echo "  ./deploy-no-gateway.sh"
    exit 1
fi

print_success "Services verified"
echo "  Backend: $BACKEND_URL"
echo "  Frontend: $FRONTEND_URL"

# Create Network Endpoint Groups
print_status "Creating Network Endpoint Groups"

if resource_exists "network-endpoint-groups" "aialchemy-backend-neg" "--region=$REGION"; then
    print_warning "Backend NEG already exists"
else
    gcloud compute network-endpoint-groups create aialchemy-backend-neg \
        --region=$REGION \
        --network-endpoint-type=serverless \
        --cloud-run-service=aialchemy-backend
    print_success "Backend NEG created"
fi

if resource_exists "network-endpoint-groups" "aialchemy-frontend-neg" "--region=$REGION"; then
    print_warning "Frontend NEG already exists"
else
    gcloud compute network-endpoint-groups create aialchemy-frontend-neg \
        --region=$REGION \
        --network-endpoint-type=serverless \
        --cloud-run-service=aialchemy-frontend
    print_success "Frontend NEG created"
fi

# Create Backend Services
print_status "Creating backend services"

# API Backend Service
if resource_exists "backend-services" "aialchemy-api-backend" "--global"; then
    print_warning "API backend service already exists"
else
    gcloud compute backend-services create aialchemy-api-backend \
        --global \
        --protocol=HTTPS \
        --enable-cdn \
        --cache-mode=USE_ORIGIN_HEADERS
    print_success "API backend service created"
fi

# Add backend to API service
gcloud compute backend-services add-backend aialchemy-api-backend \
    --global \
    --network-endpoint-group=aialchemy-backend-neg \
    --network-endpoint-group-region=$REGION 2>/dev/null || print_warning "Backend already added to API service"

# Frontend Backend Service
if resource_exists "backend-services" "aialchemy-frontend-backend" "--global"; then
    print_warning "Frontend backend service already exists"
else
    gcloud compute backend-services create aialchemy-frontend-backend \
        --global \
        --protocol=HTTPS \
        --enable-cdn \
        --cache-mode=CACHE_ALL_STATIC
    print_success "Frontend backend service created"
fi

# Add backend to frontend service
gcloud compute backend-services add-backend aialchemy-frontend-backend \
    --global \
    --network-endpoint-group=aialchemy-frontend-neg \
    --network-endpoint-group-region=$REGION 2>/dev/null || print_warning "Backend already added to frontend service"

# Create URL Map
print_status "Creating URL map for traffic routing"
cat > /tmp/aialchemy-url-map.yaml << EOF
name: aialchemy-url-map
defaultService: projects/$PROJECT_ID/global/backendServices/aialchemy-frontend-backend
hostRules:
- hosts:
  - '$DOMAIN_NAME'
  pathMatcher: aialchemy-matcher
pathMatchers:
- name: aialchemy-matcher
  defaultService: projects/$PROJECT_ID/global/backendServices/aialchemy-frontend-backend
  pathRules:
  - paths:
    - /api/*
    - /docs*
    - /redoc*
    - /openapi.json
    - /health
    service: projects/$PROJECT_ID/global/backendServices/aialchemy-api-backend
  - paths:
    - /*
    service: projects/$PROJECT_ID/global/backendServices/aialchemy-frontend-backend
EOF

gcloud compute url-maps import aialchemy-url-map \
    --source=/tmp/aialchemy-url-map.yaml \
    --global || print_warning "URL map already exists, updated"
print_success "URL map configured"

# Create SSL Certificate
print_status "Creating SSL certificate for $DOMAIN_NAME"
if resource_exists "ssl-certificates" "aialchemy-ssl-cert" "--global"; then
    print_warning "SSL certificate already exists"
else
    gcloud compute ssl-certificates create aialchemy-ssl-cert \
        --domains=$DOMAIN_NAME \
        --global
    print_success "SSL certificate created (will provision after DNS setup)"
fi

# Create HTTPS Target Proxy
print_status "Creating HTTPS target proxy"
if resource_exists "target-https-proxies" "aialchemy-https-proxy" ""; then
    print_warning "HTTPS proxy already exists"
else
    gcloud compute target-https-proxies create aialchemy-https-proxy \
        --ssl-certificates=aialchemy-ssl-cert \
        --url-map=aialchemy-url-map
    print_success "HTTPS target proxy created"
fi

# Create Global Forwarding Rule
print_status "Creating global forwarding rule"
if resource_exists "forwarding-rules" "aialchemy-https-rule" "--global"; then
    print_warning "Forwarding rule already exists"
else
    gcloud compute forwarding-rules create aialchemy-https-rule \
        --global \
        --target-https-proxy=aialchemy-https-proxy \
        --ports=443
    print_success "Global forwarding rule created"
fi

# Get External IP
EXTERNAL_IP=$(gcloud compute forwarding-rules describe aialchemy-https-rule --global --format='value(IPAddress)')

# Cleanup temp files
rm -f /tmp/aialchemy-url-map.yaml

echo ""
echo "🎉 Load Balancer Setup Complete!"
echo "================================"
print_success "External IP: $EXTERNAL_IP"
print_success "Domain: https://$DOMAIN_NAME"
echo ""

echo "📋 NEXT STEPS:"
echo "1. Configure DNS:"
echo "   Record Type: A"
echo "   Name: $DOMAIN_NAME"
echo "   Value: $EXTERNAL_IP"
echo ""
echo "2. Wait for SSL certificate provisioning (15-60 minutes after DNS)"
echo ""
echo "3. Test your setup:"
echo "   Frontend: https://$DOMAIN_NAME"
echo "   API: https://$DOMAIN_NAME/api/"
echo "   Docs: https://$DOMAIN_NAME/docs"
echo ""

echo "🔍 Monitoring Commands:"
echo "# Check SSL certificate status"
echo "gcloud compute ssl-certificates describe aialchemy-ssl-cert --global"
echo ""
echo "# Check load balancer components"
echo "gcloud compute url-maps list"
echo "gcloud compute backend-services list"
echo ""
echo "# View load balancer logs"
echo "gcloud logs read 'resource.type=http_load_balancer' --limit=10"
echo ""

# Check SSL certificate status
print_status "Checking SSL certificate status"
SSL_STATUS=$(gcloud compute ssl-certificates describe aialchemy-ssl-cert --global --format='value(managed.status)' 2>/dev/null || echo "UNKNOWN")
echo "Current SSL status: $SSL_STATUS"

if [ "$SSL_STATUS" = "PROVISIONING" ]; then
    print_warning "SSL certificate is provisioning. Configure DNS and wait 15-60 minutes."
elif [ "$SSL_STATUS" = "ACTIVE" ]; then
    print_success "SSL certificate is active! Your site should be accessible."
elif [ "$SSL_STATUS" = "FAILED_NOT_VISIBLE" ]; then
    print_error "SSL provisioning failed. Check DNS configuration."
fi

echo ""
print_success "Setup script completed successfully! 🚀"