#!/bin/bash
# AIAlchemy GCP Deployment Script - No Gateway Mode
# Deploy backend and frontend to Google Cloud Run without load balancer

set -e

# Configuration
PROJECT_ID="aialchemy-prod"
REGION="us-central1"
BACKEND_SERVICE="aialchemy-backend"
FRONTEND_SERVICE="aialchemy-frontend"

echo "🚀 Starting AIAlchemy deployment to GCP (No Gateway Mode)..."
echo "This will deploy backend and frontend services without a load balancer."
echo ""

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

echo ""
echo "🎉 AIAlchemy Deployment Complete! (No Gateway Mode)"
echo "=================================================="
echo ""
echo "📊 Your service URLs:"
echo "  🔧 Backend API:  $BACKEND_URL"
echo "  🎨 Frontend:     $FRONTEND_URL"  
echo "  📚 API Docs:     $BACKEND_URL/docs"
echo "  🔍 Health Check: $BACKEND_URL/health"
echo ""
echo "🔗 Access your application:"
echo "  Open: $FRONTEND_URL"
echo ""
echo "📊 Monitor your services:"
echo "  gcloud run services list"
echo "  gcloud logs tail 'resource.type=cloud_run_revision'"
echo ""
echo "🔄 Update services:"
echo "  Backend:  cd backend && gcloud run deploy $BACKEND_SERVICE --source ."
echo "  Frontend: cd frontend && gcloud run deploy $FRONTEND_SERVICE --source ."
echo ""
echo "🌐 Want a single domain? Set up the gateway later:"
echo "  1. Configure your domain name"
echo "  2. Run: DOMAIN_NAME=yourdomain.com ./deploy-gcp.sh"
echo "  3. See docs/DOMAIN_SETUP.md for detailed instructions"
echo ""
echo "Happy coding! 🚀"