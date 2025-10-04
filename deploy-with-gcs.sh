#!/bin/bash
# AIAlchemy Deployment with Google Cloud Storage Integration
# This script deploys the full stack including file storage capabilities

set -e

# Configuration
PROJECT_ID="${PROJECT_ID:-$(gcloud config get-value project)}"
REGION="${REGION:-us-central1}"
BACKEND_SERVICE="aialchemy-backend"
FRONTEND_SERVICE="aialchemy-frontend" 
GATEWAY_SERVICE="aialchemy-gateway"

# GCS Configuration
GCS_BUCKET_PREFIX="aialchemy-uploads"
SERVICE_ACCOUNT_NAME="aialchemy-storage"
SERVICE_ACCOUNT_KEY_FILE="gcs-service-account-key.json"

echo "🚀 Deploying AIAlchemy with Google Cloud Storage integration..."
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo ""

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Verify prerequisites
echo "🔍 Checking prerequisites..."
if ! command_exists gcloud; then
    echo "❌ Google Cloud CLI not found. Please install it first."
    exit 1
fi

if ! command_exists docker; then
    echo "❌ Docker not found. Please install it first." 
    exit 1
fi

# Verify authentication
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q "."; then
    echo "❌ Not authenticated with Google Cloud. Run 'gcloud auth login'"
    exit 1
fi

echo "✅ Prerequisites verified"

# Check if GCS is already set up
echo ""
echo "🗂️ Checking Google Cloud Storage setup..."

# Check if service account exists
if gcloud iam service-accounts describe ${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com >/dev/null 2>&1; then
    echo "✅ Service account exists: ${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
    
    # Find existing bucket or create new one
    EXISTING_BUCKET=$(gsutil ls -p $PROJECT_ID | grep "gs://${GCS_BUCKET_PREFIX}" | head -1 | sed 's|gs://||' | sed 's|/||' || echo "")
    
    if [ -n "$EXISTING_BUCKET" ]; then
        GCS_BUCKET_NAME="$EXISTING_BUCKET"
        echo "✅ Found existing bucket: gs://$GCS_BUCKET_NAME"
    else
        GCS_BUCKET_NAME="${GCS_BUCKET_PREFIX}-$(date +%s)"
        echo "⚠️ No bucket found, will create: gs://$GCS_BUCKET_NAME"
        NEED_BUCKET_SETUP=true
    fi
    
    # Check if service account key exists
    if [ -f "$SERVICE_ACCOUNT_KEY_FILE" ]; then
        echo "✅ Service account key found: $SERVICE_ACCOUNT_KEY_FILE"
        GCS_SETUP_COMPLETE=true
    else
        echo "⚠️ Service account key not found: $SERVICE_ACCOUNT_KEY_FILE"
        echo "📋 Please run: gcloud iam service-accounts keys create ./$SERVICE_ACCOUNT_KEY_FILE --iam-account=${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
        NEED_KEY_SETUP=true
    fi
else
    echo "⚠️ GCS service account not found. Please run the GCS setup commands first."
    echo "📋 See: ./GCS_SETUP_COMMANDS.md for complete setup instructions"
    
    read -p "🤔 Continue deployment without GCS? (files will use local storage) [y/N]: " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Deployment cancelled. Please set up GCS first."
        exit 1
    fi
    
    echo "⚠️ Continuing with local storage (not recommended for production)"
    USE_GCS=false
fi

# Create bucket if needed
if [ "$NEED_BUCKET_SETUP" = true ]; then
    echo ""
    echo "🪣 Creating GCS bucket..."
    
    gsutil mb -p $PROJECT_ID -c STANDARD -l $REGION gs://$GCS_BUCKET_NAME
    
    # Set CORS policy
    cat > /tmp/cors.json << 'EOF'
[
  {
    "origin": ["*"],
    "method": ["GET", "POST", "PUT", "DELETE", "HEAD"], 
    "responseHeader": ["Content-Type", "Access-Control-Allow-Origin", "x-goog-resumable"],
    "maxAgeSeconds": 3600
  }
]
EOF
    gsutil cors set /tmp/cors.json gs://$GCS_BUCKET_NAME
    
    echo "✅ Bucket created and configured: gs://$GCS_BUCKET_NAME"
fi

# Generate service account key if needed
if [ "$NEED_KEY_SETUP" = true ]; then
    echo ""
    echo "🔑 Generating service account key..."
    
    gcloud iam service-accounts keys create ./$SERVICE_ACCOUNT_KEY_FILE \
        --iam-account=${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com
    
    echo "✅ Service account key generated: $SERVICE_ACCOUNT_KEY_FILE"
    GCS_SETUP_COMPLETE=true
fi

# Enable required APIs
echo ""
echo "📡 Enabling required APIs..."
gcloud services enable run.googleapis.com \
    cloudbuild.googleapis.com \
    artifactregistry.googleapis.com \
    storage.googleapis.com

# Create Artifact Registry repository
echo ""
echo "🏭 Setting up Artifact Registry..."
REPO_NAME="aialchemy-repo"

if ! gcloud artifacts repositories describe $REPO_NAME --location=$REGION >/dev/null 2>&1; then
    gcloud artifacts repositories create $REPO_NAME \
        --repository-format=docker \
        --location=$REGION \
        --description="AIAlchemy Docker images"
    echo "✅ Artifact Registry repository created"
else
    echo "✅ Artifact Registry repository exists"
fi

# Configure Docker authentication
gcloud auth configure-docker ${REGION}-docker.pkg.dev

# Build and deploy backend
echo ""
echo "🔧 Building and deploying backend..."
cd backend

docker build -t ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/backend:latest .
docker push ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/backend:latest

# Prepare environment variables for Cloud Run
ENV_VARS="DATABASE_URL=sqlite:///./aialchemy.db"

if [ "$GCS_SETUP_COMPLETE" = true ]; then
    ENV_VARS="${ENV_VARS},USE_GOOGLE_CLOUD_STORAGE=true"
    ENV_VARS="${ENV_VARS},GOOGLE_CLOUD_STORAGE_BUCKET=${GCS_BUCKET_NAME}"
    ENV_VARS="${ENV_VARS},GOOGLE_CLOUD_PROJECT=${PROJECT_ID}"
    echo "✅ GCS environment variables configured"
else
    ENV_VARS="${ENV_VARS},USE_GOOGLE_CLOUD_STORAGE=false"
    ENV_VARS="${ENV_VARS},LOCAL_UPLOAD_PATH=/tmp/uploads"
    echo "⚠️ Using local storage (files will be lost on container restart)"
fi

gcloud run deploy $BACKEND_SERVICE \
    --image ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/backend:latest \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 1 \
    --min-instances 0 \
    --max-instances 10 \
    --port 8000 \
    --set-env-vars="$ENV_VARS"

BACKEND_URL=$(gcloud run services describe $BACKEND_SERVICE --platform managed --region $REGION --format 'value(status.url)')
echo "✅ Backend deployed: $BACKEND_URL"

cd ..

# Build and deploy frontend  
echo ""
echo "🎨 Building and deploying frontend..."
cd frontend

docker build -t ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/frontend:latest .
docker push ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/frontend:latest

gcloud run deploy $FRONTEND_SERVICE \
    --image ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/frontend:latest \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --memory 1Gi \
    --cpu 1 \
    --min-instances 0 \
    --max-instances 5 \
    --port 3000 \
    --set-env-vars="REACT_APP_API_URL=/api"

FRONTEND_URL=$(gcloud run services describe $FRONTEND_SERVICE --platform managed --region $REGION --format 'value(status.url)')
echo "✅ Frontend deployed: $FRONTEND_URL"

cd ..

# Build and deploy nginx gateway
echo ""
echo "🌐 Building and deploying nginx gateway..."
cd nginx-gateway

# Extract hostnames from URLs
BACKEND_HOST=$(echo $BACKEND_URL | sed 's|https://||')
FRONTEND_HOST=$(echo $FRONTEND_URL | sed 's|https://||')

docker build -t ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/nginx-gateway:latest .
docker push ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/nginx-gateway:latest

gcloud run deploy $GATEWAY_SERVICE \
    --image ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/nginx-gateway:latest \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --memory 512Mi \
    --cpu 1 \
    --min-instances 0 \
    --max-instances 3 \
    --port 8080 \
    --set-env-vars="BACKEND_HOST=${BACKEND_HOST},FRONTEND_HOST=${FRONTEND_HOST}"

GATEWAY_URL=$(gcloud run services describe $GATEWAY_SERVICE --platform managed --region $REGION --format 'value(status.url)')
echo "✅ Nginx gateway deployed: $GATEWAY_URL"

cd ..

# Display deployment summary
echo ""
echo "🎉 Deployment Complete!"
echo "================================="
echo "🌐 Application URL: $GATEWAY_URL"
echo "🔧 Backend API: $BACKEND_URL"  
echo "🎨 Frontend: $FRONTEND_URL"
echo ""
echo "📊 Test endpoints:"
echo "- Health check: $GATEWAY_URL/health"
echo "- API status: $GATEWAY_URL/api/status"
echo "- Dashboard: $GATEWAY_URL/"
echo ""

if [ "$GCS_SETUP_COMPLETE" = true ]; then
    echo "🗂️ File Storage:"
    echo "- Bucket: gs://$GCS_BUCKET_NAME"
    echo "- Test upload: $GATEWAY_URL/api/uploads/startup/1/files"
    echo ""
fi

echo "💰 Estimated monthly cost: ~$25 (with nginx gateway)"
echo "📝 Service URLs saved for GitHub Actions deployment"
echo ""
echo "⚠️ Important:"
echo "- Keep service account key secure: $SERVICE_ACCOUNT_KEY_FILE" 
echo "- Monitor storage costs in GCP console"
echo "- Set up budget alerts for cost control"