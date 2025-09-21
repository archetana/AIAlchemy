# AIAlchemy GCP Deployment Guide

## 🚀 Overview
This guide covers deploying the AIAlchemy platform to Google Cloud Platform (GCP) using modern cloud services.

## 📋 Prerequisites
- GCP Account with billing enabled
- Google Cloud CLI installed locally
- Node.js 18+ and Python 3.9+ installed locally
- Docker installed (for containerization)

## 🏗️ Architecture Options

### Option 1: Cloud Run + Cloud SQL (Recommended)
**Best for**: Production deployment with auto-scaling
```
Frontend (React) → Cloud Run
Backend (FastAPI) → Cloud Run  
Database → Cloud SQL (PostgreSQL)
Static Assets → Cloud Storage + CDN
```

### Option 2: App Engine (Simple)
**Best for**: Quick deployment and prototyping
```
Frontend → App Engine Standard (Node.js)
Backend → App Engine Standard (Python)
Database → Cloud SQL (PostgreSQL) or Firestore
```

### Option 3: GKE (Enterprise)
**Best for**: Large scale, microservices architecture
```
Frontend + Backend → Google Kubernetes Engine
Database → Cloud SQL or Cloud Spanner
```

## 🚀 Quick Deploy: Cloud Run (Recommended)

### Step 1: Project Setup
```bash
# Create new GCP project
gcloud projects create aialchemy-prod --name="AIAlchemy Production"

# Set project as default
gcloud config set project aialchemy-prod

# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable sql-component.googleapis.com
gcloud services enable storage-component.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

### Step 2: Database Setup (Cloud SQL PostgreSQL)
```bash
# Create PostgreSQL instance
gcloud sql instances create aialchemy-db \
    --database-version=POSTGRES_14 \
    --tier=db-f1-micro \
    --region=us-central1 \
    --root-password=YOUR_SECURE_PASSWORD

# Create application database
gcloud sql databases create aialchemy --instance=aialchemy-db

# Create database user
gcloud sql users create aialchemy-user \
    --instance=aialchemy-db \
    --password=YOUR_APP_PASSWORD
```

### Step 3: Backend Deployment
```bash
# Clone repository
git clone https://github.com/archetana/AIAlchemy.git
cd AIAlchemy

# Create Dockerfile for backend
cat > backend/Dockerfile << 'EOF'
FROM python:3.9-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8080

# Start command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
EOF

# Create requirements.txt for backend
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
EOF

# Deploy backend to Cloud Run
cd backend
gcloud run deploy aialchemy-backend \
    --source . \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --set-env-vars DATABASE_URL=postgresql://aialchemy-user:YOUR_APP_PASSWORD@/aialchemy?host=/cloudsql/aialchemy-prod:us-central1:aialchemy-db \
    --add-cloudsql-instances aialchemy-prod:us-central1:aialchemy-db
```

### Step 4: Frontend Deployment
```bash
# Create production environment file
cat > frontend/.env.production << 'EOF'
REACT_APP_API_URL=https://aialchemy-backend-HASH-uc.a.run.app
REACT_APP_NAME=AIAlchemy
REACT_APP_VERSION=1.0.0
REACT_APP_ENVIRONMENT=production
EOF

# Create Dockerfile for frontend
cat > frontend/Dockerfile << 'EOF'
FROM node:18-alpine as builder

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 8080
CMD ["nginx", "-g", "daemon off;"]
EOF

# Create nginx configuration
cat > frontend/nginx.conf << 'EOF'
events {
    worker_connections 1024;
}
http {
    include /etc/nginx/mime.types;
    server {
        listen 8080;
        root /usr/share/nginx/html;
        index index.html;
        
        location / {
            try_files $uri $uri/ /index.html;
        }
        
        location /api {
            proxy_pass $REACT_APP_API_URL;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }
}
EOF

# Deploy frontend to Cloud Run
cd frontend
gcloud run deploy aialchemy-frontend \
    --source . \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated
```

## 🔧 Alternative: App Engine Deployment

### Backend (App Engine Python)
```bash
# Create app.yaml for backend
cat > backend/app.yaml << 'EOF'
runtime: python39

env_variables:
  DATABASE_URL: postgresql://aialchemy-user:YOUR_APP_PASSWORD@/aialchemy?host=/cloudsql/aialchemy-prod:us-central1:aialchemy-db

automatic_scaling:
  min_instances: 1
  max_instances: 10

resources:
  cpu: 1
  memory_gb: 1
  disk_size_gb: 10
EOF

# Deploy backend
cd backend
gcloud app deploy
```

### Frontend (App Engine Node.js)
```bash
# Create app.yaml for frontend
cat > frontend/app.yaml << 'EOF'
runtime: nodejs18

env_variables:
  REACT_APP_API_URL: https://aialchemy-prod.uc.r.appspot.com

automatic_scaling:
  min_instances: 1
  max_instances: 5
EOF

# Create server.js for production serving
cat > frontend/server.js << 'EOF'
const express = require('express');
const path = require('path');
const app = express();

app.use(express.static(path.join(__dirname, 'build')));

app.get('/*', (req, res) => {
  res.sendFile(path.join(__dirname, 'build', 'index.html'));
});

const port = process.env.PORT || 8080;
app.listen(port, () => {
  console.log(`Server running on port ${port}`);
});
EOF

# Update package.json for production
npm install express

# Build and deploy
npm run build
gcloud app deploy
```

## 🗄️ Database Migration

### Convert SQLite to PostgreSQL
```bash
# Install conversion tools
pip install sqlite-dump

# Export data from SQLite
sqlite-dump backend/aialchemy.db > data.sql

# Import to PostgreSQL (modify connection string)
psql "postgresql://aialchemy-user:PASSWORD@/aialchemy?host=/cloudsql/PROJECT:REGION:INSTANCE" < data.sql
```

### Update Backend for PostgreSQL
```python
# Update backend/app/database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Use Cloud SQL connection in production
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./aialchemy.db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
```

## 🔒 Environment Variables Setup
```bash
# Backend environment variables
gcloud run services update aialchemy-backend \
    --set-env-vars \
    DATABASE_URL="postgresql://user:pass@/db?host=/cloudsql/project:region:instance" \
    JWT_SECRET_KEY="your-jwt-secret" \
    ENVIRONMENT="production"

# Frontend environment variables (built into container)
# Set in .env.production before building
```

## 📊 Monitoring & Logging
```bash
# Enable monitoring
gcloud services enable monitoring.googleapis.com
gcloud services enable logging.googleapis.com

# View logs
gcloud logs tail "resource.type=cloud_run_revision AND resource.labels.service_name=aialchemy-backend"
```

## 🌍 Custom Domain Setup
```bash
# Map custom domain
gcloud run domain-mappings create \
    --service aialchemy-frontend \
    --domain yourdomain.com \
    --region us-central1

# Add SSL certificate (automatic with Cloud Run)
```

## 💰 Cost Optimization
- Use Cloud Run (pay per request) for variable traffic
- Choose appropriate Cloud SQL tier (start with db-f1-micro)
- Enable Cloud Storage for static assets
- Set up Cloud CDN for global distribution
- Configure auto-scaling limits

## 🔐 Security Best Practices
- Enable Cloud IAM for API access
- Use Cloud Secret Manager for sensitive data
- Configure Cloud Armor for DDoS protection
- Enable audit logging
- Set up VPC networking for database security

## 📈 Performance Optimization
- Enable Cloud CDN for frontend assets
- Configure database connection pooling
- Use Cloud Load Balancer for high availability
- Set up Cloud Memorystore for caching
- Enable compression and minification

## 🚀 Deployment Commands Summary
```bash
# Quick deployment (Cloud Run)
./deploy-to-gcp.sh

# Check status
gcloud run services list

# View logs
gcloud logs tail

# Update service
gcloud run deploy SERVICE_NAME --source .
```

## 📝 Notes
- Replace placeholder values (PROJECT_ID, passwords, etc.)
- Adjust instance sizes based on expected traffic
- Consider using Cloud Build for CI/CD pipeline
- Set up monitoring alerts for production
- Regular database backups with Cloud SQL

This deployment guide provides multiple options for different use cases. Cloud Run is recommended for most production deployments due to its simplicity and cost-effectiveness.