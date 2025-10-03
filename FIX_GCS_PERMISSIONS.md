# 🔧 Fix GCS Permissions Issue

The `roles/storage.legacyBucketReader` role is deprecated. Here's the corrected command to fix your permissions:

## ✅ Run This Corrected Command:

```bash
# Set your environment (if not already set)
export PROJECT_ID="$(gcloud config get-value project)"

# Remove the old binding (if it was partially applied)
gcloud projects remove-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:aialchemy-storage@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/storage.legacyBucketReader" 2>/dev/null || true

# Add the correct modern role
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:aialchemy-storage@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/storage.admin"

# Verify the permissions
echo "✅ Verifying permissions..."
gcloud projects get-iam-policy $PROJECT_ID \
    --flatten="bindings[].members" \
    --format="table(bindings.role)" \
    --filter="bindings.members:aialchemy-storage@$PROJECT_ID.iam.gserviceaccount.com"
```

## 📋 Updated Role Explanation:

- **`roles/storage.objectAdmin`**: Can create, read, update, delete objects
- **`roles/storage.admin`**: Can manage buckets AND objects (replaces the deprecated legacyBucketReader)

## 🔄 Alternative Minimal Permissions (More Secure):

If you prefer minimal permissions, use these instead:

```bash
# Remove storage.admin if you added it
gcloud projects remove-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:aialchemy-storage@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/storage.admin"

# Add minimal required permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:aialchemy-storage@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/storage.objectAdmin"

# Add bucket viewer permission (modern replacement for legacyBucketReader)
gsutil iam ch serviceAccount:aialchemy-storage@$PROJECT_ID.iam.gserviceaccount.com:objectAdmin gs://$BUCKET_NAME
gsutil iam ch serviceAccount:aialchemy-storage@$PROJECT_ID.iam.gserviceaccount.com:legacyBucketReader gs://$BUCKET_NAME
```

## ⚠️ Note:
The `storage.admin` role is broader but simpler to manage. For production, you might want to use the minimal permissions approach for better security.

## ✅ Continue Setup:
After fixing the permissions, continue with the remaining steps from the original setup:

```bash
# Generate service account key (if not done)
gcloud iam service-accounts keys create ./gcs-service-account-key.json \
    --iam-account=aialchemy-storage@$PROJECT_ID.iam.gserviceaccount.com

# Test bucket access
echo "Test file content for AIAlchemy" | gsutil cp - gs://$BUCKET_NAME/test-file.txt
gsutil cat gs://$BUCKET_NAME/test-file.txt
gsutil rm gs://$BUCKET_NAME/test-file.txt

echo "✅ GCS setup completed successfully!"
```