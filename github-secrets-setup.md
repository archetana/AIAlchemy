# GitHub Secrets Setup Guide for AIAlchemy

## 🔐 Required GitHub Secrets

### Step 1: Create Google Cloud Service Account

```bash
# Set your project ID (replace with your actual project ID)
export PROJECT_ID="your-project-id-here"

# Set the project
gcloud config set project $PROJECT_ID

# Create service account for GitHub Actions
gcloud iam service-accounts create github-actions-sa \
    --description="GitHub Actions service account for AIAlchemy" \
    --display-name="GitHub Actions SA"

# Get the service account email
export SA_EMAIL="github-actions-sa@$PROJECT_ID.iam.gserviceaccount.com"

# Assign required roles
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

# Create and download service account key
gcloud iam service-accounts keys create github-actions-key.json \
    --iam-account=$SA_EMAIL

echo "✅ Service account created and key downloaded to github-actions-key.json"
```

### Step 2: Add Secrets to GitHub

#### Secret 1: GCP_PROJECT_ID
```
Name: GCP_PROJECT_ID
Value: your-actual-project-id
```

#### Secret 2: GCP_SA_KEY
```
Name: GCP_SA_KEY
Value: (entire contents of github-actions-key.json file)
```

**How to get the key content:**
```bash
# Display the JSON key content (copy this entire output)
cat github-actions-key.json
```

#### Secret 3: GCP_APP_SA_KEY (for application runtime - IMPORTANT)
```bash
# Create application service account first
export APP_SA_EMAIL="aialchemy-app-sa@$PROJECT_ID.iam.gserviceaccount.com"

gcloud iam service-accounts create aialchemy-app-sa \
    --description="AIAlchemy app runtime" \
    --display-name="AIAlchemy App SA"

# Grant necessary permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$APP_SA_EMAIL" \
    --role="roles/cloudsql.client"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$APP_SA_EMAIL" \
    --role="roles/secretmanager.secretAccessor"

# Create key
gcloud iam service-accounts keys create aialchemy-app-key.json \
    --iam-account=$APP_SA_EMAIL

# Display key content to copy
cat aialchemy-app-key.json
```

```
Name: GCP_APP_SA_KEY  
Value: (entire contents of aialchemy-app-key.json file above)
```

### Step 3: Verify Secrets Are Added

Go to your GitHub repository:
1. Settings → Secrets and variables → Actions
2. You should see:
   - ✅ GCP_PROJECT_ID
   - ✅ GCP_SA_KEY
   - ✅ GCP_APP_SA_KEY (optional)

## 🚀 Ready for Deployment

Once secrets are configured, any push to `main` branch will trigger automatic deployment!