# 🚀 AIAlchemy Production Deployment Steps

## Prerequisites Check ✅

Before deployment, ensure you have:
- [ ] Google Cloud account with billing enabled
- [ ] GitHub repository with code (✅ Done - https://github.com/archetana/AIAlchemy)
- [ ] Domain name (optional)

## 🔐 Step 1: Configure GitHub Secrets (REQUIRED)

### 1.1 Create Google Cloud Project and Service Account

```bash
# 1. Create a new GCP project (or use existing)
export PROJECT_ID="aialchemy-$(date +%s)"  # Or your chosen project ID
gcloud projects create $PROJECT_ID --name="AIAlchemy Production"
gcloud config set project $PROJECT_ID

# 2. Enable billing (MUST be done via console)
echo "🔔 IMPORTANT: Enable billing at https://console.cloud.google.com/billing/linkedaccount?project=$PROJECT_ID"
echo "Press Enter after enabling billing..."
read

# 3. Enable required APIs
gcloud services enable \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    sql-component.googleapis.com \
    sqladmin.googleapis.com \
    storage.googleapis.com \
    secretmanager.googleapis.com \
    artifactregistry.googleapis.com \
    iam.googleapis.com

# 4. Create service account for GitHub Actions
gcloud iam service-accounts create github-actions-sa \
    --description="GitHub Actions CI/CD service account" \
    --display-name="GitHub Actions SA"

export SA_EMAIL="github-actions-sa@$PROJECT_ID.iam.gserviceaccount.com"

# 5. Assign required permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/cloudbuild.builds.editor"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/run.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/storage.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/artifactregistry.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/iam.serviceAccountUser"

# 6. Generate service account key
gcloud iam service-accounts keys create github-sa-key.json \
    --iam-account=$SA_EMAIL

echo "✅ Service account created. Key saved to github-sa-key.json"
echo "📋 Your PROJECT_ID: $PROJECT_ID"
```

### 1.2 Add Secrets to GitHub Repository

**Go to: https://github.com/archetana/AIAlchemy/settings/secrets/actions**

**Add these secrets:**

1. **GCP_PROJECT_ID**
   ```
   Name: GCP_PROJECT_ID
   Value: [your-project-id from above]
   ```

2. **GCP_SA_KEY**
   ```bash
   # Copy the entire content of this file:
   cat github-sa-key.json
   ```
   ```
   Name: GCP_SA_KEY
   Value: [entire JSON content from github-sa-key.json]
   ```

## 🏗️ Step 2: Set Up Google Cloud Infrastructure

### 2.1 Create Required Infrastructure

```bash
# 1. Create Artifact Registry for Docker images
gcloud artifacts repositories create aialchemy-repo \
    --repository-format=docker \
    --location=us-central1 \
    --description="AIAlchemy Docker images"

# 2. Create Cloud SQL database (optional - for production data)
gcloud sql instances create aialchemy-db \
    --database-version=POSTGRES_15 \
    --tier=db-f1-micro \
    --region=us-central1 \
    --storage-type=SSD \
    --storage-size=10GB \
    --deletion-protection

# Set database password
export DB_PASSWORD=$(openssl rand -base64 32)
gcloud sql users set-password postgres \
    --instance=aialchemy-db \
    --password="$DB_PASSWORD"

# Create application database
gcloud sql databases create aialchemy --instance=aialchemy-db

# Create application user
gcloud sql users create aialchemy-user \
    --instance=aialchemy-db \
    --password="$DB_PASSWORD"

# 3. Create secrets for database connection
echo "postgresql://aialchemy-user:$DB_PASSWORD@/aialchemy?host=/cloudsql/$PROJECT_ID:us-central1:aialchemy-db" | \
    gcloud secrets create database-url --data-file=-

echo "your-super-secure-jwt-secret-$(openssl rand -base64 32)" | \
    gcloud secrets create jwt-secret --data-file=-

echo "✅ Infrastructure created successfully!"
echo "📋 Database connection name: $PROJECT_ID:us-central1:aialchemy-db"
```

### 2.2 Create Application Service Account (Runtime)

```bash
# Create service account for the running application
gcloud iam service-accounts create aialchemy-app-sa \
    --description="AIAlchemy application runtime service account" \
    --display-name="AIAlchemy App SA"

export APP_SA_EMAIL="aialchemy-app-sa@$PROJECT_ID.iam.gserviceaccount.com"

# Grant necessary permissions for the app
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$APP_SA_EMAIL" \
    --role="roles/cloudsql.client"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$APP_SA_EMAIL" \
    --role="roles/secretmanager.secretAccessor"

echo "✅ Application service account created: $APP_SA_EMAIL"
```

## 🚀 Step 3: Deploy Using GitHub Actions

### 3.1 Add GitHub Actions Workflow

Since we couldn't push the workflow file due to permissions, create it manually:

1. **Go to your GitHub repo**: https://github.com/archetana/AIAlchemy
2. **Create new file**: Click "Add file" → "Create new file"
3. **File path**: `.github/workflows/deploy.yml`
4. **Content**: Use the simplified workflow below

### 3.2 Simplified GitHub Actions Workflow

```yaml
name: 🚀 Deploy AIAlchemy to GCP

on:
  push:
    branches: [main]

env:
  PROJECT_ID: ${{ secrets.GCP_PROJECT_ID }}
  GAR_LOCATION: us-central1
  REPOSITORY: aialchemy-repo
  REGION: us-central1

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: 📥 Checkout code
        uses: actions/checkout@v4

      - name: 🔐 Google Auth
        uses: google-github-actions/auth@v1
        with:
          credentials_json: ${{ secrets.GCP_SA_KEY }}

      - name: 🛠️ Set up Cloud SDK
        uses: google-github-actions/setup-gcloud@v1

      - name: 🐳 Configure Docker
        run: gcloud auth configure-docker us-central1-docker.pkg.dev

      - name: 🏗️ Build and Push Backend
        run: |
          cd backend
          docker build -t us-central1-docker.pkg.dev/$PROJECT_ID/aialchemy-repo/backend:$GITHUB_SHA .
          docker push us-central1-docker.pkg.dev/$PROJECT_ID/aialchemy-repo/backend:$GITHUB_SHA

      - name: 🏗️ Build and Push Frontend
        run: |
          cd frontend
          docker build -t us-central1-docker.pkg.dev/$PROJECT_ID/aialchemy-repo/frontend:$GITHUB_SHA .
          docker push us-central1-docker.pkg.dev/$PROJECT_ID/aialchemy-repo/frontend:$GITHUB_SHA

      - name: 🚀 Deploy Backend to Cloud Run
        run: |
          gcloud run deploy aialchemy-backend \
            --image=us-central1-docker.pkg.dev/$PROJECT_ID/aialchemy-repo/backend:$GITHUB_SHA \
            --region=$REGION \
            --service-account=aialchemy-app-sa@$PROJECT_ID.iam.gserviceaccount.com \
            --set-env-vars="ENVIRONMENT=production,GOOGLE_CLOUD_PROJECT=$PROJECT_ID" \
            --memory=2Gi \
            --cpu=2 \
            --min-instances=1 \
            --max-instances=10 \
            --allow-unauthenticated

      - name: 🚀 Deploy Frontend to Cloud Run
        run: |
          BACKEND_URL=$(gcloud run services describe aialchemy-backend --region=$REGION --format='value(status.url)')
          
          gcloud run deploy aialchemy-frontend \
            --image=us-central1-docker.pkg.dev/$PROJECT_ID/aialchemy-repo/frontend:$GITHUB_SHA \
            --region=$REGION \
            --set-env-vars="REACT_APP_API_BASE_URL=$BACKEND_URL,REACT_APP_ENVIRONMENT=production" \
            --memory=1Gi \
            --cpu=1 \
            --min-instances=1 \
            --max-instances=5 \
            --allow-unauthenticated

      - name: 🎉 Get URLs
        run: |
          echo "🌐 Backend URL: $(gcloud run services describe aialchemy-backend --region=$REGION --format='value(status.url)')"
          echo "🌐 Frontend URL: $(gcloud run services describe aialchemy-frontend --region=$REGION --format='value(status.url)')"
```

## 🎯 Step 4: Trigger Deployment

### 4.1 Push to Main Branch

Once you've:
1. ✅ Added GitHub secrets
2. ✅ Created GCP infrastructure  
3. ✅ Added the workflow file

**Simply push to main branch:**
```bash
# Make any small change and push
git add .
git commit -m "🚀 Trigger production deployment"
git push origin main
```

### 4.2 Monitor Deployment

1. **Watch GitHub Actions**: Go to your repo → "Actions" tab
2. **Monitor progress**: You'll see the deployment pipeline running
3. **Check logs**: Click on the running workflow to see detailed logs

## 🏥 Step 5: Verify Deployment

### 5.1 Check Services

```bash
# List deployed services
gcloud run services list --region=us-central1

# Get service URLs
gcloud run services describe aialchemy-backend --region=us-central1 --format='value(status.url)'
gcloud run services describe aialchemy-frontend --region=us-central1 --format='value(status.url)'
```

### 5.2 Test Endpoints

```bash
# Test backend health
curl https://[your-backend-url]/health

# Test frontend
curl https://[your-frontend-url]
```

## 🎉 Success Checklist

- [ ] GitHub secrets configured
- [ ] GCP infrastructure created
- [ ] GitHub Actions workflow added
- [ ] Deployment triggered and successful
- [ ] Backend service accessible
- [ ] Frontend service accessible
- [ ] Services can communicate

## 🆘 Troubleshooting

### Common Issues:

1. **"Permission denied"**: Check service account roles
2. **"Image not found"**: Verify Artifact Registry setup
3. **"Service timeout"**: Check memory/CPU settings
4. **"Database connection failed"**: Verify Cloud SQL setup

### Get Help:
```bash
# View service logs
gcloud logs read "resource.type=cloud_run_revision" --limit=50

# Check service status  
gcloud run services describe [service-name] --region=us-central1
```

---

🚀 **Once deployed, your AIAlchemy platform will be live at the generated Cloud Run URLs!**