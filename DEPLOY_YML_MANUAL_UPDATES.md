# 🔧 Manual Updates Required for deploy.yml

Due to GitHub App permissions, the `.github/workflows/deploy.yml` file needs to be updated manually.

## 🚨 Critical Fix Required

### **Line ~104: Backend DATABASE_URL**

**CHANGE THIS:**
```yaml
--set-env-vars="DATABASE_URL=sqlite+aiosqlite:///./aialchemy.db,USE_GOOGLE_CLOUD_STORAGE=true,...
```

**TO THIS:**
```yaml
--set-env-vars="DATABASE_URL=sqlite+aiosqlite://./aialchemy.db,USE_GOOGLE_CLOUD_STORAGE=true,...
```

**Why:** Remove the extra slash (`///` → `//`) to fix the database connection error.

### **Line ~99: Frontend Port (Already Fixed?)**

Ensure the frontend deployment uses:
```yaml
--port 8080 \
--timeout 300 \
```

## 🔍 How to Update

1. **Go to your repository**: https://github.com/archetana/AIAlchemy
2. **Navigate to**: `.github/workflows/deploy.yml`
3. **Edit the file** directly on GitHub
4. **Find line ~104** with `DATABASE_URL=sqlite+aiosqlite:///./aialchemy.db`
5. **Remove one slash** to make it `DATABASE_URL=sqlite+aiosqlite://./aialchemy.db`
6. **Commit the change**

## ✅ Verification

After the fix, the logs should show:
```
📍 Using database URL: sqlite:///./aialchemy.db
✅ Database tables created successfully!
```

Instead of:
```
❌ Failed to create tables: (sqlite3.OperationalError) unable to open database file
```

## 🎯 Complete Fixed Line Should Be:

```yaml
gcloud run deploy ${{ env.BACKEND_SERVICE }} \
  --image ${{ env.REGION }}-docker.pkg.dev/${{ env.PROJECT_ID }}/${{ env.REPO_NAME }}/backend:latest \
  --platform managed \
  --region ${{ env.REGION }} \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 1 \
  --timeout 900 \
  --min-instances 0 \
  --max-instances 10 \
  --port 8080 \
  --set-env-vars="DATABASE_URL=sqlite+aiosqlite://./aialchemy.db,USE_GOOGLE_CLOUD_STORAGE=true,GOOGLE_CLOUD_STORAGE_BUCKET=${{ secrets.GCS_BUCKET_NAME }},GOOGLE_CLOUD_PROJECT=${{ secrets.GOOGLE_CLOUD_PROJECT }},SECRET_KEY=${{ secrets.SECRET_KEY }},JWT_SECRET_KEY=${{ secrets.JWT_SECRET_KEY }},ENVIRONMENT=production,DEBUG=false,BUCKET_APP_STORAGE=${{ secrets.GCS_BUCKET_NAME }},VERTEX_AI_PROJECT=${{ secrets.GOOGLE_CLOUD_PROJECT }},VERTEX_AI_LOCATION=us-central1,GCS_SERVICE_ACCOUNT_KEY_BASE64=$(cat gcs_key_base64.txt)"
```

## 🚀 After Update

Once fixed, your deployment should:
- ✅ Start backend container successfully
- ✅ Create database tables without errors  
- ✅ Pass health checks on port 8080
- ✅ Handle file uploads to GCS

The backend startup logs will show success instead of the SQLite errors you've been experiencing.