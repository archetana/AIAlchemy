# How to Get GCP_APP_SA_KEY

## What is GCP_APP_SA_KEY?

The `GCP_APP_SA_KEY` is a service account key for your **application runtime** - this is the service account that your deployed AIAlchemy application will use to access Google Cloud services like:
- Cloud SQL database
- Secret Manager
- Cloud Storage
- AI/ML APIs (Vertex AI, Document AI, etc.)

## Step-by-Step Guide

### Step 1: Create Application Service Account

```bash
# Set your project ID (use the same one from deployment setup)
export PROJECT_ID="your-project-id-here"
gcloud config set project $PROJECT_ID

# Create the application service account
gcloud iam service-accounts create aialchemy-app-sa \
    --description="AIAlchemy application runtime service account" \
    --display-name="AIAlchemy App Service Account"

# Set the service account email variable
export APP_SA_EMAIL="aialchemy-app-sa@$PROJECT_ID.iam.gserviceaccount.com"

echo "✅ Application service account created: $APP_SA_EMAIL"
```

### Step 2: Grant Required Permissions

```bash
# Grant permissions for database access
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$APP_SA_EMAIL" \
    --role="roles/cloudsql.client"

# Grant permissions for secrets access
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$APP_SA_EMAIL" \
    --role="roles/secretmanager.secretAccessor"

# Grant permissions for storage access
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$APP_SA_EMAIL" \
    --role="roles/storage.objectAdmin"

# Grant permissions for AI/ML services (for your multi-agent system)
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

echo "✅ Permissions granted to application service account"
```

### Step 3: Generate and Download the Key

```bash
# Create and download the service account key
gcloud iam service-accounts keys create aialchemy-app-key.json \
    --iam-account=$APP_SA_EMAIL

echo "✅ Service account key created: aialchemy-app-key.json"
```

### Step 4: Get the Key Content for GitHub Secret

```bash
# Display the JSON key content (copy this entire output)
echo ""
echo "🔐 GCP_APP_SA_KEY Secret Content:"
echo "=================================="
cat aialchemy-app-key.json
echo "=================================="
echo ""
echo "📋 Copy the entire JSON content above and add it as GCP_APP_SA_KEY secret in GitHub"
```

## Add to GitHub Secrets

1. **Go to**: https://github.com/archetana/AIAlchemy/settings/secrets/actions
2. **Click**: "New repository secret"
3. **Name**: `GCP_APP_SA_KEY`
4. **Value**: Paste the entire JSON content from the output above

## Simplified Version (All-in-One Command)

If you want to run everything at once:

```bash
#!/bin/bash
# Replace with your actual project ID
export PROJECT_ID="your-project-id-here"
gcloud config set project $PROJECT_ID

# Create service account
gcloud iam service-accounts create aialchemy-app-sa \
    --description="AIAlchemy app runtime SA" \
    --display-name="AIAlchemy App SA"

export APP_SA_EMAIL="aialchemy-app-sa@$PROJECT_ID.iam.gserviceaccount.com"

# Grant all necessary roles at once
for role in \
    "roles/cloudsql.client" \
    "roles/secretmanager.secretAccessor" \
    "roles/storage.objectAdmin" \
    "roles/aiplatform.user" \
    "roles/documentai.apiUser" \
    "roles/speech.editor" \
    "roles/dialogflow.reader"
do
    gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:$APP_SA_EMAIL" \
        --role="$role"
done

# Create key
gcloud iam service-accounts keys create aialchemy-app-key.json \
    --iam-account=$APP_SA_EMAIL

echo ""
echo "🎉 SUCCESS! Your GCP_APP_SA_KEY content:"
echo "========================================"
cat aialchemy-app-key.json
echo "========================================"
```

## Important Notes

### When do you need GCP_APP_SA_KEY?

- **Required if**: Your app needs to access Google Cloud services at runtime
- **Optional if**: You're just doing basic deployment without database/AI features
- **Recommended**: Always set it up for production applications

### Security Best Practices

1. **Never commit** the JSON key file to git
2. **Store securely** in GitHub Secrets only
3. **Rotate keys** periodically for security
4. **Use least privilege** - only grant necessary permissions

### What happens if you don't set it?

- Your app will deploy successfully
- But it won't be able to access Google Cloud services
- You'll see authentication errors when trying to use database, AI APIs, etc.

## Quick Test

After setting up the key, you can test it works:

```bash
# Test the service account has correct permissions
gcloud auth activate-service-account --key-file=aialchemy-app-key.json
gcloud projects get-iam-policy $PROJECT_ID --flatten="bindings[].members" --filter="bindings.members:aialchemy-app-sa@*"
```

## Summary

The `GCP_APP_SA_KEY` is essential for your AIAlchemy application to access Google Cloud services. Follow the steps above to create it, and your deployed application will be able to use databases, AI services, and storage seamlessly!