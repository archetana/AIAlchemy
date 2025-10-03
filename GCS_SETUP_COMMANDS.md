# Google Cloud Storage Setup Commands for AIAlchemy

**Execute these commands manually in your terminal in the order listed below.**

## Prerequisites

Ensure you have:
- Google Cloud SDK installed (`gcloud` command available)
- Authenticated with Google Cloud (`gcloud auth login`)
- Set your project ID (`gcloud config set project YOUR_PROJECT_ID`)

---

## Step 1: Set Environment Variables

Run these first to set up your project configuration:

```bash
# Replace with your actual project ID
export PROJECT_ID="your-project-id-here"

# Generate a unique bucket name with timestamp
export BUCKET_NAME="aialchemy-uploads-$(date +%s)"

# Display the values
echo "Project ID: $PROJECT_ID"
echo "Bucket Name: $BUCKET_NAME"

# Verify your current project
gcloud config get-value project
```

---

## Step 2: Enable Required Google Cloud APIs

```bash
echo "🔧 Enabling required APIs..."

gcloud services enable storage.googleapis.com
gcloud services enable iam.googleapis.com
gcloud services enable cloudbuild.googleapis.com

echo "✅ APIs enabled successfully"
```

---

## Step 3: Create Storage Bucket

```bash
echo "🪣 Creating storage bucket..."

gsutil mb -p $PROJECT_ID -c STANDARD -l us-central1 gs://$BUCKET_NAME

# Verify bucket creation
gsutil ls gs://$BUCKET_NAME

echo "✅ Bucket created: gs://$BUCKET_NAME"
```

---

## Step 4: Configure Bucket Policies

### 4a: Set CORS Policy for Web Uploads

```bash
echo "🌐 Setting up CORS policy..."

# Create CORS configuration file
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

# Apply CORS policy
gsutil cors set /tmp/cors.json gs://$BUCKET_NAME

# Verify CORS policy
gsutil cors get gs://$BUCKET_NAME

echo "✅ CORS policy configured"
```

### 4b: Set Lifecycle Policy for Cost Optimization

```bash
echo "♻️ Setting up lifecycle policy..."

# Create lifecycle configuration
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

# Apply lifecycle policy
gsutil lifecycle set /tmp/lifecycle.json gs://$BUCKET_NAME

# Verify lifecycle policy
gsutil lifecycle get gs://$BUCKET_NAME

echo "✅ Lifecycle policy configured"
```

---

## Step 5: Create Service Account

```bash
echo "👤 Creating service account..."

# Create service account
gcloud iam service-accounts create aialchemy-storage \
    --display-name="AIAlchemy Storage Service Account" \
    --description="Service account for file upload and storage operations"

# Verify service account creation
gcloud iam service-accounts list --filter="displayName:AIAlchemy Storage Service Account"

echo "✅ Service account created"
```

---

## Step 6: Grant Storage Permissions

```bash
echo "🔐 Granting storage permissions..."

# Grant storage object admin permissions (can create, read, update, delete objects)
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:aialchemy-storage@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/storage.objectAdmin"

# Grant storage admin permissions (can manage buckets and objects)
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:aialchemy-storage@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/storage.admin"

# Verify permissions
gcloud projects get-iam-policy $PROJECT_ID \
    --flatten="bindings[].members" \
    --format="table(bindings.role)" \
    --filter="bindings.members:aialchemy-storage@$PROJECT_ID.iam.gserviceaccount.com"

echo "✅ Permissions granted"
```

---

## Step 7: Generate Service Account Key

```bash
echo "🔑 Generating service account key..."

# Generate and download service account key
gcloud iam service-accounts keys create ./gcs-service-account-key.json \
    --iam-account=aialchemy-storage@$PROJECT_ID.iam.gserviceaccount.com

# Verify key file was created
ls -la ./gcs-service-account-key.json

echo "✅ Service account key generated: ./gcs-service-account-key.json"
echo "⚠️  Keep this key file secure and do not commit it to version control!"
```

---

## Step 8: Test Bucket Access

```bash
echo "🧪 Testing bucket access..."

# Test write access
echo "Test file content for AIAlchemy" | gsutil cp - gs://$BUCKET_NAME/test-file.txt

# Test read access
gsutil cat gs://$BUCKET_NAME/test-file.txt

# Test list access
gsutil ls gs://$BUCKET_NAME/

# Clean up test file
gsutil rm gs://$BUCKET_NAME/test-file.txt

echo "✅ Bucket access test successful"
```

---

## Step 9: Set Up Environment Variables

```bash
echo "📝 Environment variables to configure:"

cat << EOF

Add these to your .env file or deployment environment:

# Google Cloud Storage Configuration
USE_GOOGLE_CLOUD_STORAGE=true
GOOGLE_CLOUD_STORAGE_BUCKET=$BUCKET_NAME
GOOGLE_APPLICATION_CREDENTIALS=./gcs-service-account-key.json
GOOGLE_CLOUD_PROJECT=$PROJECT_ID

# For local development (.env file):
echo "USE_GOOGLE_CLOUD_STORAGE=true" >> .env
echo "GOOGLE_CLOUD_STORAGE_BUCKET=$BUCKET_NAME" >> .env
echo "GOOGLE_APPLICATION_CREDENTIALS=./gcs-service-account-key.json" >> .env
echo "GOOGLE_CLOUD_PROJECT=$PROJECT_ID" >> .env

EOF
```

---

## Step 10: Security Recommendations

```bash
echo "🔒 Security setup recommendations:"

cat << 'EOF'

1. Secure the service account key:
   - Never commit gcs-service-account-key.json to version control
   - Add it to .gitignore
   - For production, use Workload Identity instead of key files

2. Set up bucket notifications (optional):
   - Configure notifications for file upload events
   - Integrate with Cloud Functions for processing

3. Enable audit logging:
   gcloud logging sinks create aialchemy-storage-audit \
     bigquery.googleapis.com/projects/PROJECT_ID/datasets/audit_logs \
     --log-filter='resource.type="gcs_bucket" AND resource.labels.bucket_name="BUCKET_NAME"'

4. Set up monitoring:
   - Configure alerts for failed uploads
   - Monitor storage costs and usage
   - Set up budget alerts

EOF
```

---

## Summary

After running all commands above, you should have:

✅ **Storage bucket created**: `gs://aialchemy-uploads-TIMESTAMP`  
✅ **Service account**: `aialchemy-storage@PROJECT_ID.iam.gserviceaccount.com`  
✅ **Permissions configured**: Storage object admin + bucket reader  
✅ **Security policies**: CORS for web uploads, lifecycle for cost optimization  
✅ **Service account key**: `./gcs-service-account-key.json`  
✅ **Environment variables**: Ready for backend configuration  

## Next Steps

1. **Run all the commands above in order**
2. **Save the bucket name and configure environment variables**
3. **Test the backend file upload system with GCS**
4. **Deploy to Cloud Run with GCS integration**

**Copy the bucket name for configuration:**
```bash
echo "Your bucket name: $BUCKET_NAME"
```