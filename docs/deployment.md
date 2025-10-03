# AIAlchemy Deployment Guide

Complete deployment guide for AIAlchemy across different environments and platforms.

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Production Deployment (GCP)](#-production-deployment-gcp)
- [Nginx Gateway Setup](#-nginx-gateway-setup)
- [Database Configuration](#-database-configuration)
- [GitHub Actions CI/CD](#-github-actions-cicd)
- [Manual Deployment](#-manual-deployment)
- [Troubleshooting](#-troubleshooting)

## 🚀 Quick Start

### Prerequisites

- Google Cloud Platform account with billing enabled
- `gcloud` CLI installed and authenticated
- Docker installed
- Domain name (optional, for Load Balancer deployment)

### One-Click Deployment

**Option 1: Nginx Gateway (Recommended - No domain required)**
```bash
git clone https://github.com/archetana/AIAlchemy.git
cd AIAlchemy
gcloud auth login
gcloud auth application-default login
./deploy-nginx-gateway.sh
```

**Option 2: Load Balancer (Enterprise - Requires domain)**
```bash
git clone https://github.com/archetana/AIAlchemy.git
cd AIAlchemy
gcloud auth login
gcloud auth application-default login
DOMAIN_NAME=yourdomain.com ./deploy-gcp.sh
```

## 🌐 Production Deployment (GCP)

### Architecture Overview

```
Internet → Cloud Load Balancer/Nginx Gateway
├── Frontend (React) → Cloud Run
├── Backend (FastAPI) → Cloud Run
└── Database (SQLite/Cloud SQL)
```

### Cost Comparison

| Component | Nginx Gateway | Load Balancer |
|-----------|---------------|---------------|
| **Gateway** | ~$5/month | ~$25/month |
| **SSL Certificates** | Free (Let's Encrypt) | Free (Google-managed) |
| **CDN** | Basic | Global CDN |
| **Domain Required** | No | Yes |
| **Total Monthly** | ~$25 | ~$45 |

### Deployment Steps

#### 1. Setup Google Cloud Project

```bash
# Create new project (optional)
gcloud projects create aialchemy-prod --name="AIAlchemy Production"
gcloud config set project aialchemy-prod

# Enable required APIs
gcloud services enable \
    run.googleapis.com \
    artifactregistry.googleapis.com \
    cloudbuild.googleapis.com \
    compute.googleapis.com \
    certificatemanager.googleapis.com
```

#### 2. Configure Authentication

```bash
# Authenticate with GCP
gcloud auth login
gcloud auth application-default login

# Create service account for deployment
gcloud iam service-accounts create aialchemy-deployer \
    --display-name="AIAlchemy Deployer"

# Grant necessary permissions
gcloud projects add-iam-policy-binding aialchemy-prod \
    --member="serviceAccount:aialchemy-deployer@aialchemy-prod.iam.gserviceaccount.com" \
    --role="roles/run.developer"

gcloud projects add-iam-policy-binding aialchemy-prod \
    --member="serviceAccount:aialchemy-deployer@aialchemy-prod.iam.gserviceaccount.com" \
    --role="roles/artifactregistry.admin"
```

#### 3. Deploy with Nginx Gateway (Recommended)

```bash
# Clone repository
git clone https://github.com/archetana/AIAlchemy.git
cd AIAlchemy

# Deploy with nginx gateway
./deploy-nginx-gateway.sh

# Expected output:
# ✅ Backend deployed to: https://aialchemy-backend-xxx.a.run.app
# ✅ Frontend deployed to: https://aialchemy-frontend-xxx.a.run.app
# ✅ Nginx Gateway deployed to: https://aialchemy-gateway-xxx.a.run.app
# 🌐 Access your application at: https://aialchemy-gateway-xxx.a.run.app
```

#### 4. Deploy with Load Balancer (Enterprise)

```bash
# Set your domain name
export DOMAIN_NAME=yourdomain.com

# Deploy with load balancer
./deploy-gcp.sh

# Configure DNS (after deployment)
# Create A record: yourdomain.com → [External IP from output]
```

## 🔧 Nginx Gateway Setup

The nginx gateway provides a cost-effective alternative to Google Cloud Load Balancer.

### Architecture

```
nginx-gateway (Cloud Run)
├── /* → Frontend Service
├── /api/* → Backend Service
├── /docs → Backend API Documentation
└── /health → Gateway Health Check
```

### Configuration

The nginx gateway uses the following routing rules:

```nginx
# /nginx-gateway/nginx.conf
upstream backend {
    server ${BACKEND_HOST};
}

upstream frontend {
    server ${FRONTEND_HOST};
}

server {
    listen 8080;
    server_name _;

    # Backend API routes
    location /api/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # API Documentation
    location /docs {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Frontend routes (catch-all)
    location / {
        proxy_pass http://frontend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Manual Gateway Setup

```bash
# Build and deploy nginx gateway
cd nginx-gateway

# Build Docker image
docker build -t nginx-gateway .

# Tag for Artifact Registry
docker tag nginx-gateway us-central1-docker.pkg.dev/PROJECT_ID/aialchemy-repo/nginx-gateway

# Push to registry
docker push us-central1-docker.pkg.dev/PROJECT_ID/aialchemy-repo/nginx-gateway

# Deploy to Cloud Run
gcloud run deploy aialchemy-gateway \
    --image us-central1-docker.pkg.dev/PROJECT_ID/aialchemy-repo/nginx-gateway \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --port 8080 \
    --set-env-vars="BACKEND_HOST=aialchemy-backend-xxx.a.run.app,FRONTEND_HOST=aialchemy-frontend-xxx.a.run.app"
```

## 🗄️ Database Configuration

### SQLite (Default - Recommended for MVP)

The default setup uses SQLite with persistent storage through Cloud Run volumes:

```bash
# Database is automatically initialized on startup
# Location: /app/aialchemy.db (in container)
# Persistent through Cloud Run volume mounts
```

### Cloud SQL (Production)

For production workloads, upgrade to Cloud SQL:

```bash
# Create Cloud SQL instance
gcloud sql instances create aialchemy-db \
    --database-version=POSTGRES_15 \
    --tier=db-f1-micro \
    --region=us-central1 \
    --storage-size=20GB \
    --storage-type=SSD

# Create database
gcloud sql databases create aialchemy --instance=aialchemy-db

# Create database user
gcloud sql users create aialchemy-user \
    --instance=aialchemy-db \
    --password=secure-password

# Get connection string
gcloud sql instances describe aialchemy-db --format="value(connectionName)"

# Update environment variables
# DATABASE_URL=postgresql://aialchemy-user:secure-password@/aialchemy?host=/cloudsql/PROJECT_ID:REGION:aialchemy-db
```

### Database Initialization

The application automatically initializes the database on startup:

1. **Table Creation**: SQLAlchemy creates all required tables
2. **Sample Data**: Populates with sample startup applications
3. **Health Check**: Verifies database connectivity and tables

## 🔄 GitHub Actions CI/CD

### Setup

1. **Fork the repository** on GitHub
2. **Set up secrets** in your repository settings:
   ```
   GCP_PROJECT_ID=your-project-id
   GCP_SA_KEY={"type": "service_account", ...} # Service account JSON
   DOMAIN_NAME=yourdomain.com (optional)
   ```

### Workflow Configuration

The GitHub Actions workflow (`.github/workflows/deploy.yml`) supports multiple deployment modes:

```yaml
# Manual workflow dispatch with options
on:
  workflow_dispatch:
    inputs:
      deploy_gateway:
        description: 'Deploy with gateway (true/false)'
        required: true
        default: 'true'
        type: choice
        options:
          - 'true'
          - 'false'
      domain_name:
        description: 'Domain name (required if using Load Balancer)'
        required: false
        type: string
```

### Deployment Options

**1. Nginx Gateway Deployment (Recommended)**
- Set `deploy_gateway: true`
- Leave `domain_name` empty
- Cost: ~$25/month

**2. Load Balancer Deployment (Enterprise)**
- Set `deploy_gateway: true`  
- Set `domain_name: yourdomain.com`
- Cost: ~$45/month

**3. Services Only (No Gateway)**
- Set `deploy_gateway: false`
- Manual gateway setup required

### Manual Workflow Trigger

```bash
# Trigger deployment via GitHub CLI
gh workflow run deploy.yml \
    --field deploy_gateway=true \
    --field domain_name=yourdomain.com

# Or use the GitHub web interface:
# 1. Go to Actions tab
# 2. Select "Deploy to Google Cloud Platform"
# 3. Click "Run workflow"
# 4. Set parameters and run
```

## 🛠️ Manual Deployment

### Backend Deployment

```bash
cd backend

# Build Docker image
docker build -t aialchemy-backend .

# Tag for Artifact Registry  
PROJECT_ID=$(gcloud config get-value project)
docker tag aialchemy-backend us-central1-docker.pkg.dev/$PROJECT_ID/aialchemy-repo/aialchemy-backend

# Push to registry
docker push us-central1-docker.pkg.dev/$PROJECT_ID/aialchemy-repo/aialchemy-backend

# Deploy to Cloud Run
gcloud run deploy aialchemy-backend \
    --image us-central1-docker.pkg.dev/$PROJECT_ID/aialchemy-repo/aialchemy-backend \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 1 \
    --min-instances 0 \
    --max-instances 10 \
    --port 8000 \
    --set-env-vars="DATABASE_URL=sqlite:///./aialchemy.db"
```

### Frontend Deployment

```bash
cd frontend

# Build Docker image
docker build -t aialchemy-frontend .

# Tag for Artifact Registry
PROJECT_ID=$(gcloud config get-value project)  
docker tag aialchemy-frontend us-central1-docker.pkg.dev/$PROJECT_ID/aialchemy-repo/aialchemy-frontend

# Push to registry
docker push us-central1-docker.pkg.dev/$PROJECT_ID/aialchemy-repo/aialchemy-frontend

# Deploy to Cloud Run
gcloud run deploy aialchemy-frontend \
    --image us-central1-docker.pkg.dev/$PROJECT_ID/aialchemy-repo/aialchemy-frontend \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --memory 1Gi \
    --cpu 1 \
    --min-instances 0 \
    --max-instances 5 \
    --port 3000 \
    --set-env-vars="REACT_APP_API_URL=/api"
```

## 🔍 Troubleshooting

### Common Issues

#### 1. Database Initialization Failed

**Problem**: Health check shows `tables_initialized: false`

**Solution**:
```bash
# Check backend logs
gcloud logs tail 'resource.type=cloud_run_revision AND resource.labels.service_name=aialchemy-backend'

# Look for database initialization errors
# Common causes:
# - SQLite file permissions
# - Missing database directory
# - Import path issues
```

#### 2. 500 Errors on API Endpoints

**Problem**: API returns "no such table: startup_applications"

**Solution**: Database tables not created properly
```bash
# Restart the backend service to trigger initialization
gcloud run services update aialchemy-backend --region=us-central1

# Or deploy a fresh version
./deploy-nginx-gateway.sh
```

#### 3. Frontend Can't Connect to Backend

**Problem**: CORS errors or network issues

**Solution**: Check frontend environment configuration
```bash
# Verify frontend environment variables
gcloud run services describe aialchemy-frontend --region=us-central1 --format="export"

# Should show: REACT_APP_API_URL=/api
```

#### 4. Nginx Gateway Routing Issues

**Problem**: Routes not working correctly

**Solution**: Check gateway configuration
```bash
# View gateway logs
gcloud logs tail 'resource.type=cloud_run_revision AND resource.labels.service_name=aialchemy-gateway'

# Verify environment variables
gcloud run services describe aialchemy-gateway --region=us-central1 --format="export"

# Should show: BACKEND_HOST and FRONTEND_HOST
```

#### 5. Domain SSL Certificate Issues

**Problem**: SSL certificate not provisioning

**Solution**: 
```bash
# Check certificate status
gcloud compute ssl-certificates list

# Verify DNS configuration
dig yourdomain.com

# Certificate can take 15-60 minutes to provision
```

### Health Checks

#### Backend Health
```bash
curl https://aialchemy-backend-xxx.a.run.app/health
# Should return: {"status": "healthy", "tables_initialized": true}
```

#### Frontend Health  
```bash
curl https://aialchemy-frontend-xxx.a.run.app
# Should return HTML content
```

#### Gateway Health
```bash
curl https://aialchemy-gateway-xxx.a.run.app/health
# Should return gateway status
```

### Performance Monitoring

```bash
# View Cloud Run metrics
gcloud run services describe aialchemy-backend --region=us-central1

# Monitor logs in real-time
gcloud logs tail 'resource.type=cloud_run_revision' --follow

# Check resource usage
gcloud monitoring dashboards list
```

### Scaling Configuration

```bash
# Update scaling settings
gcloud run services update aialchemy-backend \
    --region=us-central1 \
    --min-instances=1 \
    --max-instances=100 \
    --cpu-throttling \
    --memory=4Gi \
    --cpu=2

# Set concurrency limits
gcloud run services update aialchemy-backend \
    --region=us-central1 \
    --concurrency=1000
```

## 🔐 Security Configuration

### Service Account Permissions

```bash
# Minimal permissions for Cloud Run services
gcloud projects add-iam-policy-binding PROJECT_ID \
    --member="serviceAccount:aialchemy-backend@PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/cloudsql.client"

gcloud projects add-iam-policy-binding PROJECT_ID \
    --member="serviceAccount:aialchemy-backend@PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/storage.objectViewer"
```

### Network Security

```bash
# Configure VPC connector (optional)
gcloud compute networks vpc-access connectors create aialchemy-connector \
    --region=us-central1 \
    --subnet=default \
    --subnet-project=PROJECT_ID \
    --min-instances=2 \
    --max-instances=3

# Use VPC connector in Cloud Run
gcloud run services update aialchemy-backend \
    --region=us-central1 \
    --vpc-connector=aialchemy-connector \
    --vpc-egress=private-ranges-only
```

## 📊 Monitoring and Alerting

### Setup Monitoring

```bash
# Enable monitoring API
gcloud services enable monitoring.googleapis.com

# Create alerting policy for service errors
gcloud alpha monitoring policies create --policy-from-file=monitoring-policy.yaml
```

### Key Metrics to Monitor

- **Request Latency**: Response times for API endpoints
- **Error Rate**: 4xx/5xx error percentages  
- **Memory Usage**: Container memory consumption
- **CPU Usage**: Container CPU utilization
- **Database Connections**: Active database connections
- **Request Volume**: Requests per second

---

For additional help, see:
- [API Documentation](./api.md)
- [Development Guide](./development.md)
- [Architecture Overview](./architecture.md)