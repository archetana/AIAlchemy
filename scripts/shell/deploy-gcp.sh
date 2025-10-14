#!/bin/bash
# AIAlchemy GCP Deployment Script with Gateway Options
# Deploy backend, frontend, and gateway to Google Cloud Run

set -e

# Configuration
PROJECT_ID="aialchemy-prod"
REGION="us-central1"
BACKEND_SERVICE="aialchemy-backend"
FRONTEND_SERVICE="aialchemy-frontend"
GATEWAY_SERVICE="aialchemy-gateway"

# Gateway options
DEPLOY_GATEWAY="${DEPLOY_GATEWAY:-true}"  # true or false
DOMAIN_NAME="${DOMAIN_NAME:-}"  # Required for load balancer

echo "🚀 Starting AIAlchemy deployment to GCP..."
echo "Deploy Gateway: $DEPLOY_GATEWAY"
if [ "$DEPLOY_GATEWAY" = "true" ] && [ -z "$DOMAIN_NAME" ]; then
    echo "❌ Error: DOMAIN_NAME is required for Cloud Load Balancer gateway"
    echo "Usage: DOMAIN_NAME=yourdomain.com ./deploy-gcp-with-gateway.sh"
    echo "Or: DEPLOY_GATEWAY=false ./deploy-gcp-with-gateway.sh (to skip gateway)"
    exit 1
fi

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ Error: Google Cloud CLI not found. Please install it first."
    echo "Visit: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Set project
echo "📋 Setting GCP project to $PROJECT_ID..."
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "🔧 Enabling required GCP APIs..."
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable sql-component.googleapis.com

if [ "$DEPLOY_GATEWAY" = "true" ]; then
    gcloud services enable compute.googleapis.com
    gcloud services enable certificatemanager.googleapis.com
fi

# Deploy backend
echo "🚀 Deploying backend to Cloud Run..."
cd backend
gcloud run deploy $BACKEND_SERVICE \
    --source . \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --memory 512Mi \
    --cpu 1 \
    --timeout 300 \
    --max-instances 10 \
    --port 8000

# Get backend URL
BACKEND_URL=$(gcloud run services describe $BACKEND_SERVICE --region=$REGION --format='value(status.url)')
echo "✅ Backend deployed at: $BACKEND_URL"

cd ..

# Create frontend production environment
echo "⚙️ Creating frontend production environment..."
cat > frontend/.env.production << EOF
REACT_APP_API_URL=$BACKEND_URL
REACT_APP_NAME=AIAlchemy
REACT_APP_VERSION=1.0.0
REACT_APP_ENVIRONMENT=production
EOF

# Deploy frontend
echo "🎨 Deploying frontend to Cloud Run..."
cd frontend
gcloud run deploy $FRONTEND_SERVICE \
    --source . \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --memory 256Mi \
    --cpu 1 \
    --max-instances 5 \
    --port 8080

# Get frontend URL
FRONTEND_URL=$(gcloud run services describe $FRONTEND_SERVICE --region=$REGION --format='value(status.url)')
echo "✅ Frontend deployed at: $FRONTEND_URL"

cd ..

# Deploy Gateway
if [ "$DEPLOY_GATEWAY" = "true" ]; then
    echo "🌐 Setting up Cloud Load Balancer Gateway..."
    
    # Set domain name for the setup script
    export DOMAIN_NAME
    ./gateway/load-balancer-setup.sh
    
    EXTERNAL_IP=$(gcloud compute forwarding-rules describe ${GATEWAY_SERVICE}-https-rule --global --format='value(IPAddress)')
    
    echo ""
    echo "🎉 Cloud Load Balancer Deployment Complete!"
    echo "==========================================="
    echo "External IP: $EXTERNAL_IP"
    echo "Domain: https://$DOMAIN_NAME"
    echo ""
    echo "📋 IMPORTANT: Configure DNS"
    echo "Create an A record for '$DOMAIN_NAME' pointing to $EXTERNAL_IP"
    echo ""
    echo "🔀 Once DNS is configured, access your application:"
    echo "  Frontend: https://$DOMAIN_NAME"
    echo "  API: https://$DOMAIN_NAME/api/"
    echo "  Docs: https://$DOMAIN_NAME/docs"
else
    echo "🔀 Gateway deployment skipped. Access services directly:"
fi

echo ""
echo "📊 Service URLs:"
echo "  Backend:  $BACKEND_URL"
echo "  Frontend: $FRONTEND_URL"
if [ "$DEPLOY_GATEWAY" = "true" ]; then
    echo "  Gateway:  https://$DOMAIN_NAME (after DNS configuration)"
fi

echo ""
echo "📊 Monitor your services:"
echo "gcloud run services list"
if [ "$DEPLOY_GATEWAY" = "true" ]; then
    echo "gcloud compute url-maps list"
    echo "gcloud compute ssl-certificates list"
fi
echo ""
echo "📝 View logs:"
echo "gcloud logs tail 'resource.type=cloud_run_revision'"
if [ "$DEPLOY_GATEWAY" = "true" ]; then
    echo "gcloud logs tail 'resource.type=http_load_balancer'"
fi
echo ""
echo "🔄 Update services:"
echo "Backend:  cd backend && gcloud run deploy $BACKEND_SERVICE --source ."
echo "Frontend: cd frontend && gcloud run deploy $FRONTEND_SERVICE --source ."
if [ "$DEPLOY_GATEWAY" = "true" ]; then
    echo "Gateway:  DOMAIN_NAME=$DOMAIN_NAME ./gateway/load-balancer-setup.sh"
fi
echo ""
echo "Happy coding! 🚀"