# 📁 Workflow Files to Copy

Since GitHub permissions prevent direct workflow updates, these files need to be manually copied to `.github/workflows/`.

## 🔄 Manual Copy Instructions

### 1. Update Existing Workflow
**Replace** `.github/workflows/deploy.yml` with the content from:
```
workflows-to-copy/deploy.yml
```

### 2. Create New Gateway Workflow  
**Create** `.github/workflows/deploy-gateway.yml` with the content from:
```
workflows-to-copy/deploy-gateway.yml
```

## 🚀 Quick Copy Steps

### Via GitHub Web Interface:
1. Go to your repository on GitHub
2. Navigate to `.github/workflows/deploy.yml`
3. Click "Edit file" (pencil icon)
4. Replace all content with `workflows-to-copy/deploy.yml`
5. Commit the changes
6. Create new file `.github/workflows/deploy-gateway.yml`
7. Copy content from `workflows-to-copy/deploy-gateway.yml`
8. Commit the new file

### Via Git Command Line:
```bash
# Copy the updated workflows
cp workflows-to-copy/deploy.yml .github/workflows/deploy.yml
cp workflows-to-copy/deploy-gateway.yml .github/workflows/deploy-gateway.yml

# Commit the changes
git add .github/workflows/
git commit -m "feat: Add gateway deployment to GitHub Actions workflows"
git push origin main
```

## ✨ What These Workflows Add

### Updated `deploy.yml`:
- ✅ Manual trigger with gateway options
- ✅ NGINX gateway deployment  
- ✅ Cloud Load Balancer setup
- ✅ Comprehensive deployment summaries
- ✅ Conditional gateway deployment

### New `deploy-gateway.yml`:
- ✅ Gateway-only deployment
- ✅ Service validation
- ✅ Force rebuild options
- ✅ Switch between gateway types

## 🔧 Usage After Copying

### Deploy with NGINX Gateway:
1. Go to Actions tab
2. Select "Deploy AIAlchemy to GCP"  
3. Click "Run workflow"
4. Set `gateway_type: nginx`
5. Click "Run workflow"

### Deploy with Load Balancer:
1. Go to Actions tab
2. Select "Deploy AIAlchemy to GCP"
3. Click "Run workflow"  
4. Set `gateway_type: load-balancer`
5. Set `domain_name: yourdomain.com`
6. Click "Run workflow"

### Gateway-Only Updates:
1. Go to Actions tab
2. Select "Deploy Gateway Only"
3. Choose gateway type and options
4. Click "Run workflow"

## 🗑️ Cleanup

After copying the workflows, you can safely delete this `workflows-to-copy/` directory:

```bash
rm -rf workflows-to-copy/
git add -A
git commit -m "cleanup: Remove workflow copy directory"
git push origin main
```