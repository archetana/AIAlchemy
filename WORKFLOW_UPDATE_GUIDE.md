# 🔧 GitHub Actions Workflow Update Guide

## 📋 **Steps to Update deploy.yml**

### **Option 1: Replace Entire File (Recommended)**

1. **Copy the corrected workflow**:
   - Content is in `deploy-nginx-corrected.yml`
   - This is the complete, tested workflow

2. **Update your GitHub repository**:
   ```bash
   # In GitHub web interface:
   # 1. Go to .github/workflows/deploy.yml
   # 2. Click "Edit this file"
   # 3. Replace entire content with deploy-nginx-corrected.yml
   # 4. Commit changes
   ```

### **Option 2: Manual Updates to Existing deploy.yml**

If you prefer to modify existing file, make these specific changes:

#### **1. Remove API Enable Step**
```yaml
# DELETE this entire step:
- name: 🔧 Enable Required APIs
  run: |
    gcloud services enable run.googleapis.com
    gcloud services enable cloudbuild.googleapis.com
```

#### **2. Add API Verification Step**
```yaml
# ADD this step instead:
- name: 🔍 Verify Required APIs
  run: |
    echo "Checking if required APIs are enabled..."
    gcloud services list --enabled --filter="name:(run.googleapis.com OR cloudbuild.googleapis.com)" --format="table(name)" || true
    echo "Note: If APIs are missing, they should be manually enabled in GCP Console"
```

#### **3. Update Frontend Environment Variable**
```yaml
# CHANGE this line in frontend deployment:
--set-env-vars="REACT_APP_API_BASE_URL=$BACKEND_URL,REACT_APP_ENVIRONMENT=production"
# TO this:
--set-env-vars="REACT_APP_API_BASE_URL=/api,REACT_APP_ENVIRONMENT=production"
```

#### **4. Remove Load Balancer Section**
```yaml
# DELETE entire section:
- name: 🌐 Setup Cloud Load Balancer Gateway
```

#### **5. Add Nginx Gateway Steps**
```yaml
# ADD these two new steps:
- name: 🏗️ Build and Push Nginx Gateway
  run: |
    cd nginx-gateway
    docker build -t us-central1-docker.pkg.dev/$PROJECT_ID/aialchemy-repo/gateway:$GITHUB_SHA .
    docker push us-central1-docker.pkg.dev/$PROJECT_ID/aialchemy-repo/gateway:$GITHUB_SHA

- name: 🌐 Deploy Nginx Gateway
  run: |
    # Get service URLs for nginx configuration
    BACKEND_URL=$(gcloud run services describe aialchemy-backend --region=$REGION --format='value(status.url)' 2>/dev/null || echo "")
    FRONTEND_URL=$(gcloud run services describe aialchemy-frontend --region=$REGION --format='value(status.url)' 2>/dev/null || echo "")
    
    if [ -z "$BACKEND_URL" ] || [ -z "$FRONTEND_URL" ]; then
      echo "❌ Error: Backend and frontend services must be deployed before setting up gateway"
      exit 1
    fi
    
    # Extract hostnames from URLs
    BACKEND_HOST=$(echo $BACKEND_URL | sed 's|https://||')
    FRONTEND_HOST=$(echo $FRONTEND_URL | sed 's|https://||')
    
    # Deploy nginx gateway
    gcloud run deploy aialchemy-gateway \
      --image=us-central1-docker.pkg.dev/$PROJECT_ID/aialchemy-repo/gateway:$GITHUB_SHA \
      --region=$REGION \
      --set-env-vars="BACKEND_HOST=$BACKEND_HOST,FRONTEND_HOST=$FRONTEND_HOST" \
      --memory=256Mi --cpu=1 --min-instances=1 --max-instances=3 \
      --port=8080 --allow-unauthenticated
```

## ⚠️ **Before Running Workflow**

### **1. Enable APIs Manually**
Since we removed the API enable step, run these commands once:

```bash
# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com  
gcloud services enable artifactregistry.googleapis.com

# Verify APIs are enabled
gcloud services list --enabled --filter="name:(run.googleapis.com OR cloudbuild.googleapis.com OR artifactregistry.googleapis.com)"
```

### **2. Update Service Account Permissions (If Needed)**
```bash
# Add required roles to service account
PROJECT_ID="your-project-id"
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:github-actions-sa@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/run.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:github-actions-sa@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/storage.admin"
```

## 🚀 **Testing the Updated Workflow**

1. **Push changes to main branch** or **manually trigger workflow**
2. **Check GitHub Actions logs** for any errors  
3. **Verify deployment** by testing endpoints:
   ```bash
   # After successful deployment, test:
   curl https://gateway-url/health
   curl https://gateway-url/api/
   curl https://gateway-url/docs
   ```

## 🔍 **Key Differences in New Workflow**

| **Before (Load Balancer)** | **After (Nginx Gateway)** |
|----------------------------|---------------------------|
| Enables APIs automatically | Checks APIs, manual enable required |
| Creates 8+ GCP resources | Creates 1 nginx service |
| Uses `REACT_APP_API_BASE_URL=$BACKEND_URL` | Uses `REACT_APP_API_BASE_URL=/api` |
| Sets up SSL certificates | Uses Cloud Run's built-in SSL |
| Requires domain configuration | Works with any Cloud Run URL |
| ~$25/month fixed cost | ~$5/month pay-per-use |

## ✅ **Expected Results**

After successful deployment, you'll have:
- ✅ **Backend Service**: `aialchemy-backend`
- ✅ **Frontend Service**: `aialchemy-frontend`  
- ✅ **Nginx Gateway**: `aialchemy-gateway`
- ✅ **Single URL**: Access everything through gateway URL
- ✅ **Cost Savings**: ~$20/month reduction

The new workflow eliminates permission errors and deploys a cost-effective nginx gateway! 🎯