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
GATEWAY_TYPE="${GATEWAY_TYPE:-nginx}"  # nginx or load-balancer
DOMAIN_NAME="${DOMAIN_NAME:-}"  # Required for load balancer

echo "🚀 Starting AIAlchemy deployment to GCP with Gateway..."
echo "Gateway Type: $GATEWAY_TYPE"
if [ "$GATEWAY_TYPE" = "load-balancer" ] && [ -z "$DOMAIN_NAME" ]; then
    echo "❌ Error: DOMAIN_NAME is required for load-balancer gateway type"
    echo "Usage: DOMAIN_NAME=yourdomain.com GATEWAY_TYPE=load-balancer ./deploy-gcp-with-gateway.sh"
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

if [ "$GATEWAY_TYPE" = "load-balancer" ]; then
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
if [ "$GATEWAY_TYPE" = "nginx" ]; then
    echo "🌐 Deploying NGINX Gateway..."
    
    cd gateway
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
    
    GATEWAY_URL=$(gcloud run services describe $GATEWAY_SERVICE --region=$REGION --format='value(status.url)')
    cd ..
    
    echo ""
    echo "🎉 NGINX Gateway Deployment Complete!"
    echo "===================================="
    echo "Gateway URL: $GATEWAY_URL"
    echo ""
    echo "🔀 Access your application:"
    echo "  Frontend: $GATEWAY_URL"
    echo "  API: $GATEWAY_URL/api/"
    echo "  Docs: $GATEWAY_URL/docs"
    
elif [ "$GATEWAY_TYPE" = "load-balancer" ]; then
    echo "🌐 Setting up Cloud Load Balancer..."
    
    # Set domain name for the setup script
    export DOMAIN_NAME
    ./gateway/load-balancer-setup.sh
    
    EXTERNAL_IP=$(gcloud compute forwarding-rules describe ${GATEWAY_SERVICE}-https-rule --global --format='value(IPAddress)')
    
    echo ""
    echo "🎉 Load Balancer Deployment Complete!"
    echo "===================================="
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
fi

echo ""
echo "📊 Direct service URLs (for reference):"
echo "  Backend:  $BACKEND_URL"
echo "  Frontend: $FRONTEND_URL"
if [ "$GATEWAY_TYPE" = "nginx" ]; then
    echo "  Gateway:  $GATEWAY_URL"
fi

echo ""
echo "📊 Monitor your services:"
echo "gcloud run services list"
echo ""
echo "📝 View logs:"
echo "gcloud logs tail 'resource.type=cloud_run_revision'"
echo ""
echo "🔄 Update services:"
echo "Backend:  cd backend && gcloud run deploy $BACKEND_SERVICE --source ."
echo "Frontend: cd frontend && gcloud run deploy $FRONTEND_SERVICE --source ."
if [ "$GATEWAY_TYPE" = "nginx" ]; then
    echo "Gateway:  cd gateway && gcloud run deploy $GATEWAY_SERVICE --source ."
fi
echo ""
echo "Happy coding! 🚀"