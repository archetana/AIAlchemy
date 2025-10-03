# ⚡ Google Cloud Storage Setup - Execute These Commands

**Run these commands in your local terminal (NOT in the sandbox) in the exact order listed below.**

## ✅ Prerequisites Check

Before starting, ensure you have:

```bash
# 1. Check if gcloud is installed
gcloud version

# 2. Check if you're authenticated
gcloud auth list

# 3. If not authenticated, login:
gcloud auth login

# 4. Set your project (replace with your actual project ID)
gcloud config set project YOUR_PROJECT_ID
```

---

## 🚀 Quick Setup Script

**Copy and paste this entire script into your terminal:**

```bash
#!/bin/bash
# AIAlchemy GCS Quick Setup Script

# STEP 1: Set your project configuration
echo "🔧 Setting up project configuration..."
export PROJECT_ID="$(gcloud config get-value project)"
export BUCKET_NAME="aialchemy-uploads-$(date +%s)"

echo "Project ID: $PROJECT_ID"
echo "Bucket Name: $BUCKET_NAME"

# STEP 2: Enable required APIs
echo "📡 Enabling required APIs..."
gcloud services enable storage.googleapis.com
gcloud services enable iam.googleapis.com
gcloud services enable cloudbuild.googleapis.com

# STEP 3: Create storage bucket
echo "🪣 Creating storage bucket..."
gsutil mb -p $PROJECT_ID -c STANDARD -l us-central1 gs://$BUCKET_NAME

# STEP 4: Set CORS policy for web uploads
echo "🌐 Setting up CORS policy..."
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
gsutil cors set /tmp/cors.json gs://$BUCKET_NAME

# STEP 5: Set lifecycle policy for cost optimization
echo "♻️ Setting up lifecycle policy..."
cat > /tmp/lifecycle.json << 'EOF'
{
  "lifecycle": {
    "rule": [
      {
        "action": {"type": "Delete"},
        "condition": {"age": 365, "matchesStorageClass": ["STANDARD"]}
      },
      {
        "action": {"type": "SetStorageClass", "storageClass": "COLDLINE"},
        "condition": {"age": 30}
      }
    ]
  }
}
EOF
gsutil lifecycle set /tmp/lifecycle.json gs://$BUCKET_NAME

# STEP 6: Create service account
echo "👤 Creating service account..."
gcloud iam service-accounts create aialchemy-storage \
    --display-name="AIAlchemy Storage Service Account" \
    --description="Service account for file upload and storage operations"

# STEP 7: Grant storage permissions
echo "🔐 Granting storage permissions..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:aialchemy-storage@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/storage.objectAdmin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:aialchemy-storage@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/storage.legacyBucketReader"

# STEP 8: Generate service account key (navigate to your project directory first)
echo "🔑 Generating service account key..."
gcloud iam service-accounts keys create ./gcs-service-account-key.json \
    --iam-account=aialchemy-storage@$PROJECT_ID.iam.gserviceaccount.com

# STEP 9: Test bucket access
echo "🧪 Testing bucket access..."
echo "Test file content for AIAlchemy" | gsutil cp - gs://$BUCKET_NAME/test-file.txt
gsutil cat gs://$BUCKET_NAME/test-file.txt
gsutil rm gs://$BUCKET_NAME/test-file.txt

# STEP 10: Display configuration
echo ""
echo "✅ Google Cloud Storage setup completed successfully!"
echo ""
echo "📋 SAVE THESE VALUES - You'll need them for your .env file:"
echo "============================================================"
echo "GOOGLE_CLOUD_PROJECT=$PROJECT_ID"
echo "GOOGLE_CLOUD_STORAGE_BUCKET=$BUCKET_NAME"
echo "USE_GOOGLE_CLOUD_STORAGE=true"
echo "GOOGLE_APPLICATION_CREDENTIALS=./gcs-service-account-key.json"
echo ""
echo "🔒 SECURITY NOTE: The file 'gcs-service-account-key.json' has been created."
echo "   - Keep this file secure and do NOT commit it to version control"
echo "   - Add it to your .gitignore file"
echo ""
```

---

## 🛠️ Manual Step-by-Step (Alternative)

If you prefer to run commands individually, here's the breakdown:

### 1. Set Environment Variables
```bash
export PROJECT_ID="$(gcloud config get-value project)"
export BUCKET_NAME="aialchemy-uploads-$(date +%s)"
echo "Project: $PROJECT_ID"
echo "Bucket: $BUCKET_NAME"
```

### 2. Enable APIs
```bash
gcloud services enable storage.googleapis.com iam.googleapis.com cloudbuild.googleapis.com
```

### 3. Create Bucket
```bash
gsutil mb -p $PROJECT_ID -c STANDARD -l us-central1 gs://$BUCKET_NAME
```

### 4. Configure CORS
```bash
cat > /tmp/cors.json << 'EOF'
[{"origin": ["*"], "method": ["GET", "POST", "PUT", "DELETE", "HEAD"], "responseHeader": ["Content-Type", "Access-Control-Allow-Origin", "x-goog-resumable"], "maxAgeSeconds": 3600}]
EOF
gsutil cors set /tmp/cors.json gs://$BUCKET_NAME
```

### 5. Create Service Account
```bash
gcloud iam service-accounts create aialchemy-storage --display-name="AIAlchemy Storage Service Account"
```

### 6. Grant Permissions
```bash
gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:aialchemy-storage@$PROJECT_ID.iam.gserviceaccount.com" --role="roles/storage.objectAdmin"
gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:aialchemy-storage@$PROJECT_ID.iam.gserviceaccount.com" --role="roles/storage.legacyBucketReader"
```

### 7. Generate Key
```bash
gcloud iam service-accounts keys create ./gcs-service-account-key.json --iam-account=aialchemy-storage@$PROJECT_ID.iam.gserviceaccount.com
```

### 8. Test Access
```bash
echo "test" | gsutil cp - gs://$BUCKET_NAME/test.txt && gsutil rm gs://$BUCKET_NAME/test.txt
```

---

## 📝 After Setup - Configure Environment

Once you've run the setup commands, create/update your `.env` file with:

```bash
# Add these to your .env file in the backend directory
USE_GOOGLE_CLOUD_STORAGE=true
GOOGLE_CLOUD_STORAGE_BUCKET=aialchemy-uploads-XXXXXXXXXX  # Use the bucket name from output
GOOGLE_APPLICATION_CREDENTIALS=./gcs-service-account-key.json
GOOGLE_CLOUD_PROJECT=your-project-id

# Ensure these are also set
LOCAL_UPLOAD_PATH=./uploads
MAX_UPLOAD_SIZE_MB=500
MAX_DOCUMENT_SIZE_MB=50
MAX_IMAGE_SIZE_MB=10
MAX_VIDEO_SIZE_MB=500
MAX_AUDIO_SIZE_MB=100
```

## 🔒 Security Checklist

After setup, ensure:

- [ ] `gcs-service-account-key.json` is in your `.gitignore`
- [ ] Service account key is stored securely
- [ ] Bucket permissions are correctly configured
- [ ] CORS policy allows your frontend domain

## 🚀 Next Steps

1. **Execute the setup script above**
2. **Save the bucket name from the output**
3. **Update your `.env` file with the configuration**
4. **Test the backend file upload system**
5. **Deploy with GCS integration**

## ❓ Need Help?

If you encounter any issues:

1. Check `gcloud auth list` to ensure authentication
2. Verify `gcloud config get-value project` shows correct project
3. Check that required APIs are enabled: `gcloud services list --enabled`
4. Verify bucket permissions: `gsutil iam get gs://YOUR_BUCKET_NAME`

---

**Run the quick setup script above and then let me know the bucket name so I can configure the backend properly!**