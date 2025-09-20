# 🚀 AIAlchemy Quick Deploy Guide

## Copy and Run These Commands (5 minutes setup)

### 1. Create Google Cloud Project
```bash
# Set your project ID (change this to your preference)
export PROJECT_ID="aialchemy-prod-$(date +%s)"
echo "Your Project ID: $PROJECT_ID"

# Create project
gcloud projects create $PROJECT_ID --name="AIAlchemy Production"
gcloud config set project $PROJECT_ID

# IMPORTANT: Enable billing via console
echo "🔔 ENABLE BILLING: https://console.cloud.google.com/billing/linkedaccount?project=$PROJECT_ID"
echo "Press Enter after enabling billing..."
read
```

### 2. Enable APIs and Create Service Account
```bash
# Enable required APIs (takes 1-2 minutes)
gcloud services enable \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    artifactregistry.googleapis.com \
    iam.googleapis.com

# Create service account
gcloud iam service-accounts create github-actions-sa \
    --description="GitHub Actions CI/CD" \
    --display-name="GitHub Actions SA"

export SA_EMAIL="github-actions-sa@$PROJECT_ID.iam.gserviceaccount.com"

# Assign roles
gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:$SA_EMAIL" --role="roles/run.admin"
gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:$SA_EMAIL" --role="roles/artifactregistry.admin"
gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:$SA_EMAIL" --role="roles/iam.serviceAccountUser"

# Create key
gcloud iam service-accounts keys create github-key.json --iam-account=$SA_EMAIL

echo "✅ Setup complete!"
```

### 3. Create Infrastructure
```bash
# Create Docker repository
gcloud artifacts repositories create aialchemy-repo \
    --repository-format=docker \
    --location=us-central1

# Create app service account
gcloud iam service-accounts create aialchemy-app-sa \
    --display-name="AIAlchemy App SA"

echo "✅ Infrastructure ready!"
```

### 4. Get Your Secrets
```bash
echo ""
echo "🔐 ADD THESE SECRETS TO GITHUB:"
echo "================================"
echo ""
echo "Secret 1 - GCP_PROJECT_ID:"
echo "$PROJECT_ID"
echo ""
echo "Secret 2 - GCP_SA_KEY:"
echo "Copy the content below:"
cat github-key.json
echo ""
echo "================================"
echo ""
echo "🌐 Add secrets at: https://github.com/archetana/AIAlchemy/settings/secrets/actions"
```

## 🎯 Next Steps After Running Commands:

1. **Copy the output** from step 4 above
2. **Go to GitHub**: https://github.com/archetana/AIAlchemy/settings/secrets/actions
3. **Add the 2 secrets** (GCP_PROJECT_ID and GCP_SA_KEY)
4. **Create workflow file**: `.github/workflows/deploy.yml` with content from `github-workflow-simple.yml`
5. **Push to trigger deployment**:
   ```bash
   git add .
   git commit -m "🚀 Add deployment workflow"
   git push origin main
   ```

## 🎉 Result

Your AIAlchemy platform will be deployed automatically and you'll get URLs like:
- Frontend: `https://aialchemy-frontend-[random].run.app`  
- Backend: `https://aialchemy-backend-[random].run.app`

Total setup time: **~5-10 minutes** ⚡