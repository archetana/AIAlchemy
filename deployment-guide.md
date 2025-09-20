# 🚀 AIAlchemy Deployment Guide

Complete step-by-step guide for deploying AIAlchemy to Google Cloud Platform with end-to-end CI/CD.

## 📋 Prerequisites

Before starting deployment, ensure you have:

- [x] Google Cloud account with billing enabled
- [x] GitHub repository with code
- [x] Local development environment set up
- [x] Domain name (optional, for custom domains)

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   GitHub Repo   │───▶│  Cloud Build /   │───▶│   Cloud Run     │
│                 │    │  GitHub Actions  │    │   (Frontend &   │
└─────────────────┘    └──────────────────┘    │    Backend)     │
                                               └─────────────────┘
                              │
                              ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Cloud SQL     │    │   Secret Manager │    │  Artifact       │
│  (PostgreSQL)   │    │   (API Keys)     │    │  Registry       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🎯 Step 1: Google Cloud Project Setup

### 1.1 Create Project and Enable APIs

```bash
# Set variables
export PROJECT_ID="aialchemy-$(date +%s)"
export PROJECT_NAME="AIAlchemy Startup Evaluator"
export REGION="us-central1"
export ZONE="us-central1-a"

# Create project
gcloud projects create $PROJECT_ID --name="$PROJECT_NAME"
gcloud config set project $PROJECT_ID

# Enable billing (you must do this via console)
echo "🔔 Enable billing at: https://console.cloud.google.com/billing/linkedaccount?project=$PROJECT_ID"

# Enable APIs
gcloud services enable \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    sql-component.googleapis.com \
    sqladmin.googleapis.com \
    storage.googleapis.com \
    secretmanager.googleapis.com \
    aiplatform.googleapis.com \
    documentai.googleapis.com \
    speech.googleapis.com \
    dialogflow.googleapis.com \
    bigquery.googleapis.com \
    vision.googleapis.com \
    containerregistry.googleapis.com \
    artifactregistry.googleapis.com \
    cloudresourcemanager.googleapis.com \
    iam.googleapis.com \
    monitoring.googleapis.com \
    logging.googleapis.com

echo "✅ APIs enabled successfully"
```

### 1.2 Create Service Accounts

```bash
# Create service accounts
gcloud iam service-accounts create cicd-service-account \
    --description="CI/CD pipeline service account" \
    --display-name="CI/CD Service Account"

gcloud iam service-accounts create app-service-account \
    --description="Application runtime service account" \
    --display-name="App Service Account"

# Set variables
export CICD_SA_EMAIL="cicd-service-account@$PROJECT_ID.iam.gserviceaccount.com"
export APP_SA_EMAIL="app-service-account@$PROJECT_ID.iam.gserviceaccount.com"

# Assign roles to CI/CD service account
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$CICD_SA_EMAIL" \
    --role="roles/cloudbuild.builds.editor"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$CICD_SA_EMAIL" \
    --role="roles/run.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$CICD_SA_EMAIL" \
    --role="roles/storage.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$CICD_SA_EMAIL" \
    --role="roles/secretmanager.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$CICD_SA_EMAIL" \
    --role="roles/iam.serviceAccountUser"

# Assign roles to app service account
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$APP_SA_EMAIL" \
    --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$APP_SA_EMAIL" \
    --role="roles/documentai.apiUser"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$APP_SA_EMAIL" \
    --role="roles/speech.editor"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$APP_SA_EMAIL" \
    --role="roles/dialogflow.reader"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$APP_SA_EMAIL" \
    --role="roles/bigquery.dataEditor"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$APP_SA_EMAIL" \
    --role="roles/storage.objectAdmin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$APP_SA_EMAIL" \
    --role="roles/cloudsql.client"

# Generate service account keys
gcloud iam service-accounts keys create ./cicd-key.json \
    --iam-account=$CICD_SA_EMAIL

gcloud iam service-accounts keys create ./app-key.json \
    --iam-account=$APP_SA_EMAIL

echo "✅ Service accounts configured"
```

## 🗄️ Step 2: Database Setup

### 2.1 Create Cloud SQL Instance

```bash
# Create Cloud SQL instance
gcloud sql instances create aialchemy-db \
    --database-version=POSTGRES_15 \
    --tier=db-f1-micro \
    --region=$REGION \
    --storage-type=SSD \
    --storage-size=10GB \
    --storage-auto-increase \
    --backup-start-time=03:00 \
    --maintenance-window-day=SUN \
    --maintenance-window-hour=04 \
    --deletion-protection

# Set root password
export DB_ROOT_PASSWORD=$(openssl rand -base64 32)
gcloud sql users set-password postgres \
    --instance=aialchemy-db \
    --password="$DB_ROOT_PASSWORD"

# Create application database and user
gcloud sql databases create aialchemy --instance=aialchemy-db

export DB_USER_PASSWORD=$(openssl rand -base64 32)
gcloud sql users create aialchemy-user \
    --instance=aialchemy-db \
    --password="$DB_USER_PASSWORD"

# Get connection name
export DB_CONNECTION_NAME=$(gcloud sql instances describe aialchemy-db --format="value(connectionName)")

echo "✅ Database created"
echo "Connection Name: $DB_CONNECTION_NAME"
```

### 2.2 Create Staging Database (Optional)

```bash
# Create staging instance (smaller tier)
gcloud sql instances create aialchemy-db-staging \
    --database-version=POSTGRES_15 \
    --tier=db-f1-micro \
    --region=$REGION \
    --storage-type=SSD \
    --storage-size=10GB

# Configure staging database
gcloud sql databases create aialchemy --instance=aialchemy-db-staging
gcloud sql users create aialchemy-user \
    --instance=aialchemy-db-staging \
    --password="$DB_USER_PASSWORD"

echo "✅ Staging database created"
```

## 🔐 Step 3: Secrets Management

### 3.1 Create Secrets in Secret Manager

```bash
# Create database URL secrets
echo "postgresql://aialchemy-user:$DB_USER_PASSWORD@/$DB_CONNECTION_NAME/aialchemy" | \
    gcloud secrets create database-url --data-file=-

echo "postgresql://aialchemy-user:$DB_USER_PASSWORD@/$DB_CONNECTION_NAME-staging/aialchemy" | \
    gcloud secrets create database-url-staging --data-file=-

# Create other secrets (you'll need to add actual values)
echo "your-super-secure-jwt-secret-$(openssl rand -base64 32)" | \
    gcloud secrets create jwt-secret --data-file=-

echo "your-gemini-api-key" | \
    gcloud secrets create gemini-api-key --data-file=-

echo "your-crunchbase-api-key" | \
    gcloud secrets create crunchbase-api-key --data-file=-

echo "your-linkedin-api-key" | \
    gcloud secrets create linkedin-api-key --data-file=-

echo "✅ Secrets created"
```

## 🐳 Step 4: Container Registry Setup

### 4.1 Create Artifact Registry Repository

```bash
# Create Docker repository
gcloud artifacts repositories create aialchemy-repo \
    --repository-format=docker \
    --location=$REGION \
    --description="AIAlchemy Docker images"

echo "✅ Artifact Registry configured"
```

## 📦 Step 5: Storage Setup

### 5.1 Create Cloud Storage Buckets

```bash
# Create storage buckets
gsutil mb -p $PROJECT_ID -c STANDARD -l $REGION gs://$PROJECT_ID-app-storage
gsutil mb -p $PROJECT_ID -c STANDARD -l $REGION gs://$PROJECT_ID-ml-models
gsutil mb -p $PROJECT_ID -c STANDARD -l $REGION gs://$PROJECT_ID-documents
gsutil mb -p $PROJECT_ID -c STANDARD -l $REGION gs://$PROJECT_ID-build-artifacts

# Set appropriate permissions
gsutil iam ch serviceAccount:$APP_SA_EMAIL:objectAdmin gs://$PROJECT_ID-app-storage
gsutil iam ch serviceAccount:$APP_SA_EMAIL:objectAdmin gs://$PROJECT_ID-ml-models
gsutil iam ch serviceAccount:$APP_SA_EMAIL:objectAdmin gs://$PROJECT_ID-documents

echo "✅ Storage buckets created"
```

## 🚀 Step 6: GitHub Repository Setup

### 6.1 Add GitHub Secrets

Add these secrets to your GitHub repository settings:

```bash
# In GitHub repository settings > Secrets and variables > Actions

GCP_PROJECT_ID: $PROJECT_ID
GCP_SA_KEY: (contents of cicd-key.json file)
GCP_APP_SA_KEY: (contents of app-key.json file)
```

### 6.2 Configure Cloud Build Trigger (Alternative to GitHub Actions)

```bash
# Create Cloud Build trigger
gcloud builds triggers create github \
    --repo-name=AIAlchemy \
    --repo-owner=YOUR_GITHUB_USERNAME \
    --branch-pattern="^main$" \
    --build-config=cloudbuild.yaml \
    --description="Deploy AIAlchemy on main branch"

echo "✅ Cloud Build trigger created"
```

## 🏃‍♂️ Step 7: Initial Deployment

### 7.1 Manual Deploy (First Time)

```bash
# Build and deploy backend
cd backend
docker build -t $REGION-docker.pkg.dev/$PROJECT_ID/aialchemy-repo/backend:latest .
docker push $REGION-docker.pkg.dev/$PROJECT_ID/aialchemy-repo/backend:latest

gcloud run deploy aialchemy-backend \
    --image=$REGION-docker.pkg.dev/$PROJECT_ID/aialchemy-repo/backend:latest \
    --region=$REGION \
    --service-account=$APP_SA_EMAIL \
    --set-env-vars="ENVIRONMENT=production,GOOGLE_CLOUD_PROJECT=$PROJECT_ID" \
    --set-cloudsql-instances=$DB_CONNECTION_NAME \
    --memory=2Gi \
    --cpu=2 \
    --min-instances=1 \
    --max-instances=100 \
    --allow-unauthenticated

# Get backend URL
export BACKEND_URL=$(gcloud run services describe aialchemy-backend \
    --region=$REGION --format='value(status.url)')

# Build and deploy frontend
cd ../frontend
docker build -t $REGION-docker.pkg.dev/$PROJECT_ID/aialchemy-repo/frontend:latest .
docker push $REGION-docker.pkg.dev/$PROJECT_ID/aialchemy-repo/frontend:latest

gcloud run deploy aialchemy-frontend \
    --image=$REGION-docker.pkg.dev/$PROJECT_ID/aialchemy-repo/frontend:latest \
    --region=$REGION \
    --set-env-vars="REACT_APP_API_BASE_URL=$BACKEND_URL,REACT_APP_ENVIRONMENT=production" \
    --memory=2Gi \
    --cpu=2 \
    --min-instances=1 \
    --max-instances=50 \
    --allow-unauthenticated

export FRONTEND_URL=$(gcloud run services describe aialchemy-frontend \
    --region=$REGION --format='value(status.url)')

echo "🎉 Deployment completed!"
echo "Backend URL: $BACKEND_URL"
echo "Frontend URL: $FRONTEND_URL"
```

### 7.2 Test Deployment

```bash
# Test backend health
curl $BACKEND_URL/health

# Test frontend
curl $FRONTEND_URL

echo "✅ Deployment verified"
```

## 🔄 Step 8: Set Up Continuous Deployment

### 8.1 Push to Repository

```bash
# Initialize git repository (if not already done)
git init
git add .
git commit -m "Initial AIAlchemy deployment setup"

# Add remote and push
git remote add origin https://github.com/YOUR_USERNAME/AIAlchemy.git
git branch -M main
git push -u origin main
```

### 8.2 Trigger Automatic Deployment

Once you push to the main branch, the CI/CD pipeline will automatically:

1. **Build and Test** - Run all tests for backend and frontend
2. **Security Scan** - Scan containers for vulnerabilities  
3. **Deploy to Staging** - Deploy to staging environment (if develop branch)
4. **Deploy to Production** - Deploy to production (if main branch)
5. **Health Checks** - Verify deployment success

## 🎛️ Step 9: Domain Configuration (Optional)

### 9.1 Map Custom Domain

```bash
# Add custom domain to frontend service
gcloud run domain-mappings create \
    --service=aialchemy-frontend \
    --domain=yourdomain.com \
    --region=$REGION

# Add custom domain to backend service  
gcloud run domain-mappings create \
    --service=aialchemy-backend \
    --domain=api.yourdomain.com \
    --region=$REGION

echo "✅ Custom domains configured"
```

## 📊 Step 10: Monitoring and Alerting

### 10.1 Set Up Monitoring

```bash
# Create uptime checks
gcloud monitoring uptime-checks create HTTP \
    --hostname=$FRONTEND_URL \
    --path=/health \
    --display-name="AIAlchemy Frontend Health"

gcloud monitoring uptime-checks create HTTP \
    --hostname=$BACKEND_URL \
    --path=/health \
    --display-name="AIAlchemy Backend Health"

echo "✅ Monitoring configured"
```

## 🔧 Step 11: Environment Variables Summary

Create these environment configurations:

### Production Environment Variables

```bash
# Backend (.env.production)
ENVIRONMENT=production
GOOGLE_CLOUD_PROJECT=$PROJECT_ID
DATABASE_URL=projects/$PROJECT_ID/secrets/database-url/versions/latest
JWT_SECRET_KEY=projects/$PROJECT_ID/secrets/jwt-secret/versions/latest
GEMINI_API_KEY=projects/$PROJECT_ID/secrets/gemini-api-key/versions/latest

# Frontend (.env.production)  
REACT_APP_API_BASE_URL=$BACKEND_URL
REACT_APP_ENVIRONMENT=production
```

## 🎯 Deployment Checklist

- [ ] Google Cloud project created and billing enabled
- [ ] All required APIs enabled
- [ ] Service accounts created with proper permissions
- [ ] Cloud SQL database configured
- [ ] Secrets stored in Secret Manager
- [ ] Artifact Registry repository created
- [ ] Storage buckets configured
- [ ] GitHub secrets configured
- [ ] CI/CD pipeline working
- [ ] Custom domain mapped (optional)
- [ ] Monitoring and alerting configured
- [ ] Backup and disaster recovery planned

## 🚨 Important Security Notes

1. **Service Account Keys**: Store securely, rotate regularly
2. **Database Access**: Use Cloud SQL Proxy, no public IPs
3. **Secrets**: Never commit secrets to git, use Secret Manager
4. **IAM**: Follow least privilege principle
5. **HTTPS**: Always use HTTPS, disable HTTP
6. **CORS**: Configure properly for your domain

## 🔄 Ongoing Management

### Daily Operations

```bash
# Check service status
gcloud run services list

# View logs
gcloud logs read "resource.type=cloud_run_revision" --limit=100

# Monitor costs
gcloud billing budgets list

# Update secrets
echo "new-secret-value" | gcloud secrets versions add SECRET_NAME --data-file=-
```

### Scaling Configuration

```bash
# Update service scaling
gcloud run services update SERVICE_NAME \
    --min-instances=2 \
    --max-instances=200 \
    --concurrency=100
```

## 📚 Additional Resources

- [Google Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Cloud Build Documentation](https://cloud.google.com/build/docs)
- [Cloud SQL Best Practices](https://cloud.google.com/sql/docs/best-practices)
- [Secret Manager Documentation](https://cloud.google.com/secret-manager/docs)

---

🎉 **Congratulations!** Your AIAlchemy platform is now deployed on Google Cloud with full CI/CD automation.