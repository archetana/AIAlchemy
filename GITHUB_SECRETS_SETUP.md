# 🔐 GitHub Secrets Setup Guide for AIAlchemy

This guide walks you through setting up GitHub Actions secrets for secure deployment with Google Cloud Storage integration.

## 🎯 **Why Use GitHub Secrets?**

- ✅ **Security**: Keep sensitive data out of your repository
- ✅ **Compliance**: Follow security best practices
- ✅ **Flexibility**: Easy to update without code changes
- ✅ **CI/CD Ready**: Automated deployments with secure credentials

---

## 📋 **Required Secrets**

You need to add **5 secrets** to your GitHub repository:

| Secret Name | Description | Example Value |
|-------------|-------------|---------------|
| `GCS_SERVICE_ACCOUNT_KEY` | Complete JSON service account key | `{"type": "service_account",...}` |
| `GOOGLE_CLOUD_PROJECT` | Your Google Cloud project ID | `automatic-asset-472710-b6` |
| `GCS_BUCKET_NAME` | Your GCS bucket name | `aialchemy-uploads` |
| `SECRET_KEY` | Backend application secret key | `your-32-char-secret-key-here` |
| `JWT_SECRET_KEY` | JWT signing secret key | `different-32-char-jwt-key-here` |

---

## 🚀 **Step-by-Step Setup**

### **Step 1: Get Your Service Account Key Content**

```bash
# Navigate to where you stored your GCS service account key
cat gcs-service-account-key.json
```

**Copy the ENTIRE JSON output** (including the curly braces). It should look like:
```json
{
  "type": "service_account",
  "project_id": "automatic-asset-472710-b6",
  "private_key_id": "abc123...",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQ...\n-----END PRIVATE KEY-----\n",
  "client_email": "aialchemy-storage@automatic-asset-472710-b6.iam.gserviceaccount.com",
  "client_id": "123456789...",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/aialchemy-storage%40automatic-asset-472710-b6.iam.gserviceaccount.com"
}
```

### **Step 2: Add Secrets to GitHub Repository**

1. **Navigate to your repository**: https://github.com/archetana/AIAlchemy

2. **Go to Settings**:
   - Click the "⚙️ Settings" tab (top of repository page)

3. **Access Secrets**:
   - In the left sidebar, click "Secrets and variables" → "Actions"

4. **Add each secret** by clicking "New repository secret":

#### Secret 1: GCS_SERVICE_ACCOUNT_KEY
- **Name**: `GCS_SERVICE_ACCOUNT_KEY`
- **Secret**: Paste the entire JSON from Step 1
- Click "Add secret"

#### Secret 2: GOOGLE_CLOUD_PROJECT  
- **Name**: `GOOGLE_CLOUD_PROJECT`
- **Secret**: `automatic-asset-472710-b6`
- Click "Add secret"

#### Secret 3: GCS_BUCKET_NAME
- **Name**: `GCS_BUCKET_NAME`
- **Secret**: `aialchemy-uploads`
- Click "Add secret"

#### Secret 4: SECRET_KEY
- **Name**: `SECRET_KEY`
- **Secret**: Generate a 32+ character random string
- **Generate one**: `openssl rand -hex 32`
- Click "Add secret"

#### Secret 5: JWT_SECRET_KEY
- **Name**: `JWT_SECRET_KEY` 
- **Secret**: Generate another different 32+ character random string
- **Generate one**: `openssl rand -hex 32`
- Click "Add secret"

### **Step 3: Verify Secrets Are Added**

After adding all secrets, you should see:
- ✅ GCS_SERVICE_ACCOUNT_KEY
- ✅ GOOGLE_CLOUD_PROJECT
- ✅ GCS_BUCKET_NAME  
- ✅ SECRET_KEY
- ✅ JWT_SECRET_KEY

---

## 🔧 **How It Works**

### **During GitHub Actions Deployment**:

1. **Authentication**: Service account key is decoded and used for GCS access
2. **Runtime Setup**: Key is provided to Cloud Run as base64 environment variable
3. **Backend Startup**: Backend automatically configures GCS authentication
4. **File Uploads**: All file uploads go directly to your GCS bucket

### **Security Features**:

- 🔐 **No credentials in code**: Keys never appear in repository
- 🔄 **Temporary files**: Service account keys are created temporarily during deployment
- 🧹 **Automatic cleanup**: Temporary files are removed after deployment
- 🛡️ **Encrypted storage**: GitHub encrypts all secrets

---

## 🧪 **Testing the Setup**

After adding secrets and pushing code:

1. **Check Actions**: Go to "Actions" tab in your repository
2. **Monitor deployment**: Watch the "Deploy to Production with GCS" workflow
3. **Verify GCS**: Check that files are uploaded to your bucket
4. **Test endpoints**: Visit the deployed application URLs

### **Deployment will**:
- ✅ Build and deploy backend with GCS integration
- ✅ Build and deploy frontend (ESLint issues fixed)
- ✅ Configure nginx gateway
- ✅ Set up all environment variables securely
- ✅ Run health checks

---

## 🔄 **Updating Secrets**

To update any secret later:

1. Go to Settings → Secrets and variables → Actions
2. Click the secret name
3. Click "Update"
4. Enter new value
5. Click "Update secret"

---

## 🚨 **Security Best Practices**

### **✅ Do:**
- Generate strong, unique secret keys
- Rotate secrets periodically  
- Use GitHub secrets for all sensitive data
- Monitor access logs in Google Cloud Console

### **❌ Don't:**
- Put secrets in code or environment files
- Share secrets via email or chat
- Use the same secret for multiple purposes
- Commit `.env` files with real secrets

---

## 🎉 **Next Steps**

After setting up secrets:

1. **✅ Add all 5 secrets to GitHub**
2. **✅ Push code to trigger deployment**
3. **✅ Monitor GitHub Actions workflow** 
4. **✅ Test the deployed application**
5. **✅ Verify file uploads to GCS bucket**

## 📞 **Need Help?**

If you encounter issues:

1. **Check GitHub Actions logs** for detailed error messages
2. **Verify secrets** are added with correct names
3. **Test GCS access** locally with the service account key
4. **Review Cloud Run logs** in Google Cloud Console

---

**🔗 Deployment will be triggered automatically when you push to the `main` branch or create a pull request!**