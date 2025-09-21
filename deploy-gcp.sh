#!/bin/bash
# AIAlchemy GCP Deployment Script
# Quick deployment to Google Cloud Run

set -e

# Configuration
PROJECT_ID="aialchemy-prod"
REGION="us-central1"
BACKEND_SERVICE="aialchemy-backend"
FRONTEND_SERVICE="aialchemy-frontend"

echo "🚀 Starting AIAlchemy deployment to GCP..."

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

# Create backend Dockerfile
echo "🐳 Creating backend Dockerfile..."
cat > backend/Dockerfile << 'EOF'
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create uploads directory
RUN mkdir -p uploads

# Expose port (Cloud Run uses 8080 by default)
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Start command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
EOF

# Create backend requirements.txt
echo "📦 Creating backend requirements.txt..."
cat > backend/requirements.txt << 'EOF'
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
pydantic==2.5.0
python-multipart==0.0.6
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
alembic==1.12.1
aiosqlite==0.19.0
python-dotenv==1.0.0
EOF

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
    --port 8080

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

# Create frontend Dockerfile
echo "🐳 Creating frontend Dockerfile..."
cat > frontend/Dockerfile << 'EOF'
# Build stage
FROM node:18-alpine as builder

WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm ci --only=production

# Copy source code and build
COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built app
COPY --from=builder /app/build /usr/share/nginx/html

# Create nginx config
RUN echo 'server { \
    listen 8080; \
    root /usr/share/nginx/html; \
    index index.html; \
    location / { \
        try_files $uri $uri/ /index.html; \
    } \
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ { \
        expires 1y; \
        add_header Cache-Control "public, immutable"; \
    } \
}' > /etc/nginx/conf.d/default.conf

# Remove default nginx config
RUN rm /etc/nginx/conf.d/default.conf.bak 2>/dev/null || true

EXPOSE 8080
CMD ["nginx", "-g", "daemon off;"]
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

# Summary
echo ""
echo "🎉 Deployment Complete!"
echo "========================="
echo "Backend API:  $BACKEND_URL"
echo "Frontend App: $FRONTEND_URL"
echo "Swagger Docs: $BACKEND_URL/docs"
echo ""
echo "📊 Monitor your services:"
echo "gcloud run services list"
echo ""
echo "📝 View logs:"
echo "gcloud logs tail 'resource.type=cloud_run_revision'"
echo ""
echo "🔄 Update services:"
echo "cd backend && gcloud run deploy $BACKEND_SERVICE --source ."
echo "cd frontend && gcloud run deploy $FRONTEND_SERVICE --source ."
echo ""
echo "Happy coding! 🚀"