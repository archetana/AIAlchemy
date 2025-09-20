# Google Cloud Platform Setup Guide for AIAlchemy

## 🎯 Overview
This guide will help you set up a complete Google Cloud environment with CI/CD for the AIAlchemy startup evaluation platform.

## 📋 Prerequisites
- Google Cloud account with billing enabled
- GitHub repository for the project
- Local development environment with gcloud CLI

## 🚀 Step-by-Step Setup

### Step 1: Google Cloud Project Creation

#### 1.1 Create Project
```bash
# Replace with your desired project ID
export PROJECT_ID="aialchemy-evaluator-$(date +%s)"
export PROJECT_NAME="AIAlchemy Startup Evaluator"

# Create the project
gcloud projects create $PROJECT_ID --name="$PROJECT_NAME"

# Set as default project
gcloud config set project $PROJECT_ID

# Enable billing (you'll need to link billing account via console)
echo "🔔 IMPORTANT: Enable billing for project $PROJECT_ID in Google Cloud Console"
echo "🔗 https://console.cloud.google.com/billing/linkedaccount?project=$PROJECT_ID"
```

#### 1.2 Enable Required APIs
```bash
# Enable all required Google Cloud APIs
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

echo "✅ All APIs enabled successfully"
```

### Step 2: Service Accounts and IAM Configuration

#### 2.1 Create Service Accounts
```bash
# Create CI/CD service account for Cloud Build
gcloud iam service-accounts create cicd-service-account \
    --description="Service account for CI/CD pipeline" \
    --display-name="CI/CD Service Account"

# Create application service account for runtime
gcloud iam service-accounts create app-service-account \
    --description="Service account for AIAlchemy application" \
    --display-name="AIAlchemy App Service Account"

# Get service account emails
export CICD_SA_EMAIL="cicd-service-account@$PROJECT_ID.iam.gserviceaccount.com"
export APP_SA_EMAIL="app-service-account@$PROJECT_ID.iam.gserviceaccount.com"
```

#### 2.2 Assign IAM Roles
```bash
# CI/CD Service Account Permissions
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

# Application Service Account Permissions
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

echo "✅ IAM roles assigned successfully"
```

#### 2.3 Generate Service Account Keys
```bash
# Create service account key for CI/CD (for GitHub Actions)
gcloud iam service-accounts keys create ./cicd-key.json \
    --iam-account=$CICD_SA_EMAIL

# Create service account key for application runtime
gcloud iam service-accounts keys create ./app-key.json \
    --iam-account=$APP_SA_EMAIL

echo "✅ Service account keys generated"
echo "🔐 Store these keys securely and add to GitHub Secrets"
```

### Step 3: Cloud SQL Database Setup

#### 3.1 Create Cloud SQL Instance
```bash
# Create PostgreSQL instance
gcloud sql instances create aialchemy-db \
    --database-version=POSTGRES_15 \
    --tier=db-f1-micro \
    --region=us-central1 \
    --storage-type=SSD \
    --storage-size=10GB \
    --storage-auto-increase \
    --backup-start-time=03:00 \
    --maintenance-window-day=SUN \
    --maintenance-window-hour=04 \
    --maintenance-release-channel=production \
    --deletion-protection

echo "✅ Cloud SQL instance created"
```

#### 3.2 Configure Database
```bash
# Set root password (replace with secure password)
gcloud sql users set-password postgres \
    --instance=aialchemy-db \
    --password="$(openssl rand -base64 32)"

# Create application database
gcloud sql databases create aialchemy --instance=aialchemy-db

# Create application user
gcloud sql users create aialchemy-user \
    --instance=aialchemy-db \
    --password="$(openssl rand -base64 32)"

# Get connection name for later use
export DB_CONNECTION_NAME=$(gcloud sql instances describe aialchemy-db --format="value(connectionName)")
echo "Database Connection Name: $DB_CONNECTION_NAME"
```

### Step 4: Storage and Secrets Setup

#### 4.1 Create Cloud Storage Buckets
```bash
# Create bucket for application files
gsutil mb -p $PROJECT_ID -c STANDARD -l us-central1 gs://$PROJECT_ID-app-storage

# Create bucket for ML models
gsutil mb -p $PROJECT_ID -c STANDARD -l us-central1 gs://$PROJECT_ID-ml-models

# Create bucket for document processing
gsutil mb -p $PROJECT_ID -c STANDARD -l us-central1 gs://$PROJECT_ID-documents

echo "✅ Storage buckets created"
```

#### 4.2 Create Secrets in Secret Manager
```bash
# Create secrets for sensitive configuration
gcloud secrets create database-url
gcloud secrets create jwt-secret
gcloud secrets create gemini-api-key
gcloud secrets create crunchbase-api-key
gcloud secrets create linkedin-api-key

echo "✅ Secrets created in Secret Manager"
echo "📝 Remember to add actual values to these secrets"
```

### Step 5: AI/ML Services Configuration

#### 5.1 Enable Vertex AI
```bash
# Initialize Vertex AI in the region
gcloud ai index-endpoints create \
    --region=us-central1 \
    --display-name="AIAlchemy Endpoint"

echo "✅ Vertex AI initialized"
```

#### 5.2 Document AI Setup
```bash
# Note: Document AI processors need to be created via Console
echo "📝 Create Document AI processors in Google Cloud Console:"
echo "🔗 https://console.cloud.google.com/ai/document-ai/processors"
echo "   - Create 'Form Parser' processor for pitch decks"
echo "   - Create 'Document OCR' processor for general documents"
echo "   - Note down processor IDs for configuration"
```

### Step 6: Artifact Registry Setup

#### 6.1 Create Docker Repositories
```bash
# Create repository for Docker images
gcloud artifacts repositories create aialchemy-repo \
    --repository-format=docker \
    --location=us-central1 \
    --description="AIAlchemy Docker images"

echo "✅ Artifact Registry repository created"
```

### Step 7: Environment Configuration Files

#### 7.1 Development Environment
```bash
# Create .env.development template
cat > .env.development << EOF
# Development Environment Configuration
ENVIRONMENT=development
DEBUG=true

# Google Cloud Configuration
GOOGLE_CLOUD_PROJECT=$PROJECT_ID
GOOGLE_APPLICATION_CREDENTIALS=./app-key.json

# Database Configuration (use Cloud SQL Proxy for local dev)
DATABASE_URL=postgresql://aialchemy-user:PASSWORD@localhost:5432/aialchemy

# Redis Configuration (local)
REDIS_URL=redis://localhost:6379/0

# AI Services Configuration
VERTEX_AI_PROJECT=$PROJECT_ID
VERTEX_AI_LOCATION=us-central1
DOCUMENT_AI_PROCESSOR_ID=YOUR_PROCESSOR_ID
DIALOGFLOW_AGENT_ID=YOUR_AGENT_ID

# External APIs (get from respective services)
GEMINI_API_KEY=your-gemini-key
CRUNCHBASE_API_KEY=your-crunchbase-key
LINKEDIN_API_KEY=your-linkedin-key

# Security
JWT_SECRET_KEY=development-jwt-secret
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Storage
BUCKET_APP_STORAGE=$PROJECT_ID-app-storage
BUCKET_ML_MODELS=$PROJECT_ID-ml-models
BUCKET_DOCUMENTS=$PROJECT_ID-documents
EOF

echo "✅ Development environment configuration created"
```

#### 7.2 Production Environment (Cloud Run)
```bash
# Production will use Secret Manager, but here's the structure:
cat > .env.production.template << EOF
# Production Environment Configuration
ENVIRONMENT=production
DEBUG=false

# Google Cloud Configuration (injected by Cloud Run)
GOOGLE_CLOUD_PROJECT=$PROJECT_ID
GOOGLE_APPLICATION_CREDENTIALS=/var/secrets/google/key.json

# Database Configuration (Cloud SQL via Unix socket)
DATABASE_URL=postgresql://aialchemy-user:PASSWORD@/aialchemy?host=/cloudsql/$DB_CONNECTION_NAME

# Redis Configuration (Cloud Memorystore)
REDIS_URL=redis://MEMORYSTORE_IP:6379/0

# All other secrets will be injected from Secret Manager
EOF

echo "✅ Production environment template created"
```

## 🔧 Next Steps

### 1. GitHub Repository Setup
1. Push your code to GitHub repository
2. Add the following secrets to GitHub repository:
   - `GCP_SA_KEY`: Contents of `cicd-key.json`
   - `GCP_PROJECT_ID`: Your project ID
   - `GCP_APP_SA_KEY`: Contents of `app-key.json`

### 2. Local Development Setup
1. Install Cloud SQL Proxy for local database access
2. Set up local Redis instance
3. Configure service account authentication
4. Install required Python and Node.js dependencies

### 3. Deploy Application
1. Commit your Cloud Build configuration
2. Push to main branch to trigger deployment
3. Configure custom domain (optional)
4. Set up monitoring and alerting

## 📚 Useful Commands

```bash
# Check service status
gcloud run services list

# View Cloud Build logs
gcloud builds log BUILD_ID

# Connect to Cloud SQL
gcloud sql connect aialchemy-db --user=postgres

# View application logs
gcloud logs read "resource.type=cloud_run_revision" --limit=50

# Update service account permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:SERVICE_ACCOUNT_EMAIL" \
    --role="roles/ROLE_NAME"
```

## 🚨 Security Checklist

- [ ] Service account keys stored securely
- [ ] Database passwords are strong and stored in Secret Manager
- [ ] IAM permissions follow least privilege principle
- [ ] Cloud SQL has authorized networks configured
- [ ] Application secrets use Secret Manager
- [ ] Regular security audits scheduled

## 📊 Monitoring and Alerting

```bash
# Create basic alerting policy
gcloud alpha monitoring policies create \
    --policy-from-file=alerting-policy.yaml

# Set up uptime checks
gcloud monitoring uptime-checks create HTTP \
    --hostname=YOUR_CLOUD_RUN_URL \
    --path=/health
```

This comprehensive setup provides a production-ready Google Cloud environment with proper security, monitoring, and CI/CD capabilities for your AIAlchemy platform.