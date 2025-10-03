#!/bin/bash
# AIAlchemy GCP Deployment Script with Nginx Gateway
# Deploy backend, frontend, and nginx gateway to Google Cloud Run

set -e

# Configuration
PROJECT_ID="${PROJECT_ID:-aialchemy-prod}"
REGION="${REGION:-us-central1}"
BACKEND_SERVICE="aialchemy-backend"
FRONTEND_SERVICE="aialchemy-frontend"
GATEWAY_SERVICE="aialchemy-gateway"

echo "🚀 Starting AIAlchemy deployment with Nginx Gateway..."
echo "Project: $PROJECT_ID"
echo "Region: $REGION"

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
BACKEND_HOST=$(echo $BACKEND_URL | sed 's|https://||')
echo "✅ Backend deployed at: $BACKEND_URL"

cd ..

# Create frontend production environment
echo "⚙️ Creating frontend production environment..."
cat > frontend/.env.production << EOF
REACT_APP_API_URL=/api
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
FRONTEND_HOST=$(echo $FRONTEND_URL | sed 's|https://||')
echo "✅ Frontend deployed at: $FRONTEND_URL"

cd ..

# Deploy Nginx Gateway
echo "🌐 Deploying Nginx Gateway..."
cd nginx-gateway
gcloud run deploy $GATEWAY_SERVICE \
    --source . \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --memory 256Mi \
    --cpu 1 \
    --max-instances 3 \
    --port 8080 \
    --set-env-vars="BACKEND_HOST=$BACKEND_HOST,FRONTEND_HOST=$FRONTEND_HOST"

# Get gateway URL
GATEWAY_URL=$(gcloud run services describe $GATEWAY_SERVICE --region=$REGION --format='value(status.url)')
echo "✅ Gateway deployed at: $GATEWAY_URL"

cd ..

echo ""
echo "🎉 AIAlchemy Deployment Complete!"
echo "================================="
echo ""
echo "📊 Service URLs:"
echo "  🌐 Gateway (Main):   $GATEWAY_URL"
echo "  🔧 Backend (Direct): $BACKEND_URL"
echo "  🎨 Frontend (Direct): $FRONTEND_URL"
echo ""
echo "🔗 Access your application via Gateway:"
echo "  Frontend:     $GATEWAY_URL"
echo "  Backend API:  $GATEWAY_URL/api/"
echo "  API Docs:     $GATEWAY_URL/docs"
echo "  Health Check: $GATEWAY_URL/health"
echo ""
echo "💰 Cost Benefits:"
echo "  - No load balancer fees (~$25/month saved)"
echo "  - Pay-per-use pricing"
echo "  - Automatic scaling to zero"
echo ""
echo "📊 Monitor your services:"
echo "gcloud run services list --region=$REGION"
echo ""
echo "📝 View logs:"
echo "gcloud run services logs read $GATEWAY_SERVICE --region=$REGION"
echo "gcloud run services logs read $BACKEND_SERVICE --region=$REGION"
echo "gcloud run services logs read $FRONTEND_SERVICE --region=$REGION"
echo ""
echo "🔄 Update services:"
echo "Backend:  cd backend && gcloud run deploy $BACKEND_SERVICE --source . --region=$REGION"
echo "Frontend: cd frontend && gcloud run deploy $FRONTEND_SERVICE --source . --region=$REGION"
echo "Gateway:  cd nginx-gateway && gcloud run deploy $GATEWAY_SERVICE --source . --region=$REGION"
echo ""
echo "Happy coding! 🚀"