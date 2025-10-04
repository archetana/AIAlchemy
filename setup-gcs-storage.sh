#!/bin/bash
# Google Cloud Storage Setup for AIAlchemy File Uploads
# Run these commands manually in your terminal

set -e

echo "🚀 Setting up Google Cloud Storage for AIAlchemy file uploads..."

# Set your project ID (replace with your actual project)
export PROJECT_ID="your-project-id-here"
echo "Using project: $PROJECT_ID"

# 1. Enable required APIs
echo "📡 Enabling Google Cloud APIs..."
echo "Run these commands:"
echo "gcloud services enable storage.googleapis.com"
echo "gcloud services enable iam.googleapis.com" 
echo "gcloud services enable cloudbuild.googleapis.com"

echo ""
echo "2. Create storage bucket for file uploads..."
export BUCKET_NAME="aialchemy-uploads-$(date +%s)"
echo "🗂️  Creating bucket: $BUCKET_NAME"
echo "Run this command:"
echo "gsutil mb -p $PROJECT_ID -c STANDARD -l us-central1 gs://$BUCKET_NAME"

echo ""
echo "3. Set bucket permissions and lifecycle..."
echo "Run these commands:"

cat << 'EOF'
# Create lifecycle configuration
cat > lifecycle.json << 'LIFECYCLE_EOF'
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
LIFECYCLE_EOF

# Apply lifecycle policy
gsutil lifecycle set lifecycle.json gs://BUCKET_NAME
EOF

echo "Replace BUCKET_NAME with: $BUCKET_NAME"

echo ""
echo "4. Set CORS policy for web uploads..."
echo "Run these commands:"

cat << 'EOF'
# Create CORS configuration
cat > cors.json << 'CORS_EOF'
[
  {
    "origin": ["*"],
    "method": ["GET", "POST", "PUT", "DELETE", "HEAD"],
    "responseHeader": ["Content-Type", "Access-Control-Allow-Origin", "x-goog-resumable"],
    "maxAgeSeconds": 3600
  }
]
CORS_EOF

# Apply CORS policy  
gsutil cors set cors.json gs://BUCKET_NAME
EOF

echo "Replace BUCKET_NAME with: $BUCKET_NAME"

echo ""
echo "5. Create service account for file operations..."
echo "Run these commands:"

cat << EOF
# Create service account
gcloud iam service-accounts create aialchemy-storage \\
    --display-name="AIAlchemy Storage Service Account" \\
    --description="Service account for file upload and storage operations"

# Grant storage permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \\
    --member="serviceAccount:aialchemy-storage@$PROJECT_ID.iam.gserviceaccount.com" \\
    --role="roles/storage.objectAdmin"

gcloud projects add-iam-policy-binding $PROJECT_ID \\
    --member="serviceAccount:aialchemy-storage@$PROJECT_ID.iam.gserviceaccount.com" \\
    --role="roles/storage.legacyBucketReader"

# Generate service account key
gcloud iam service-accounts keys create ./gcs-service-account.json \\
    --iam-account=aialchemy-storage@$PROJECT_ID.iam.gserviceaccount.com
EOF

echo ""
echo "6. Test bucket access..."
echo "Run this command to test:"
echo "echo 'test file' | gsutil cp - gs://$BUCKET_NAME/test.txt"
echo "gsutil ls gs://$BUCKET_NAME/"
echo "gsutil rm gs://$BUCKET_NAME/test.txt"

echo ""
echo "📋 Environment Variables to Set:"
cat << EOF

# Add these to your .env file or Cloud Run environment:
USE_GOOGLE_CLOUD_STORAGE=true
GOOGLE_CLOUD_STORAGE_BUCKET=$BUCKET_NAME
GOOGLE_APPLICATION_CREDENTIALS=./gcs-service-account.json

# For Cloud Run deployment:
GOOGLE_CLOUD_PROJECT=$PROJECT_ID

EOF

echo ""
echo "📦 Required Python packages:"
echo "Add to backend/requirements.txt:"
echo "google-cloud-storage==2.10.0"

echo ""
echo "✅ Setup complete! Remember to:"
echo "1. Run all the gcloud and gsutil commands above"
echo "2. Add the environment variables to your deployment"
echo "3. Add google-cloud-storage to requirements.txt"
echo "4. Upload the service account key securely to your deployment"

echo ""
echo "🔐 Security Notes:"
echo "- Keep the service account key secure"
echo "- For Cloud Run, use workload identity instead of key files"
echo "- Set up bucket notifications for virus scanning if needed"
echo "- Consider enabling audit logging for compliance"