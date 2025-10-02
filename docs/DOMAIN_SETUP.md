# 🌐 Domain Setup for AIAlchemy Deployment

## Overview

AIAlchemy supports two deployment modes:
1. **Direct Services** - Backend and Frontend deployed separately on Cloud Run
2. **Gateway Mode** - Single domain with Cloud Load Balancer (requires domain configuration)

## 🚀 Quick Fix for Current Deployment Error

The deployment is failing because `DOMAIN_NAME` is required for gateway setup. Choose one solution:

### ✅ Solution 1: Set GitHub Secret (Recommended)

1. Go to **GitHub repository → Settings → Secrets and variables → Actions**
2. Click **"New repository secret"**
3. **Name**: `DOMAIN_NAME`
4. **Value**: Your domain (e.g., `aialchemy.example.com`)
5. Re-run the deployment

### ✅ Solution 2: Manual Workflow with Domain Input

1. Go to **GitHub repository → Actions**
2. Select **"🚀 Deploy AIAlchemy to GCP"**
3. Click **"Run workflow"**
4. Check **"Deploy/Update Cloud Load Balancer Gateway"**
5. Enter your domain in **"Domain name"** field
6. Click **"Run workflow"**

### ✅ Solution 3: Deploy Without Gateway (Temporary)

The deployment now defaults to **no gateway** to prevent the error. This deploys:
- ✅ Backend API on Cloud Run
- ✅ Frontend on Cloud Run  
- ❌ No single domain endpoint (you'll get separate URLs)

## 🌐 Setting Up Custom Domain

### Step 1: Choose Your Domain Strategy

**Option A: Use Your Own Domain**
```
yourdomain.com → AIAlchemy
api.yourdomain.com → Backend API
```

**Option B: Use Subdomain**
```
aialchemy.yourdomain.com → Frontend
aialchemy.yourdomain.com/api → Backend API
```

### Step 2: Configure DNS

After deployment with gateway enabled, you'll get an external IP. Create DNS records:

```dns
# For yourdomain.com setup:
A    yourdomain.com    →  [EXTERNAL_IP]

# For subdomain setup:  
A    aialchemy.yourdomain.com  →  [EXTERNAL_IP]
```

### Step 3: SSL Certificate

Google automatically provisions SSL certificates after DNS is configured (15-60 minutes).

## 🔧 Gateway Architecture

```
Internet → Cloud Load Balancer → SSL Certificate
    ↓
yourdomain.com/* → Frontend (React)
yourdomain.com/api/* → Backend (FastAPI)
yourdomain.com/docs → API Documentation
```

## 🎯 Benefits of Gateway Mode

- **Single Entry Point**: One domain for everything
- **SSL/TLS**: Automatic certificate management
- **CDN**: Global content delivery network
- **Load Balancing**: High availability and performance
- **Custom Routing**: Path-based traffic routing

## 📊 Deployment Commands

```bash
# Deploy without gateway (current default)
git push origin main

# Deploy with manual gateway setup
# Go to GitHub Actions → Run workflow → Enable gateway + set domain

# Local deployment with gateway
DOMAIN_NAME=yourdomain.com ./deploy-gcp.sh
```

## 🔍 Troubleshooting

### Domain Not Working After Deployment

1. **Check DNS propagation**: `nslookup yourdomain.com`
2. **Verify external IP**: `gcloud compute forwarding-rules describe aialchemy-gateway-https-rule --global`
3. **Check SSL certificate**: `gcloud compute ssl-certificates list`

### SSL Certificate Issues

```bash
# Check certificate status
gcloud compute ssl-certificates describe aialchemy-gateway-ssl-cert --global

# Common states:
# PROVISIONING → DNS configured, certificate pending
# ACTIVE → Ready to use
# FAILED_NOT_VISIBLE → DNS not configured correctly
```

### Update Domain Later

```bash
# Update existing gateway with new domain
DOMAIN_NAME=newdomain.com ./gateway/load-balancer-setup.sh
```

## 🔗 Related Documentation

- [GCP Load Balancer Setup](https://cloud.google.com/load-balancing/docs)
- [SSL Certificate Management](https://cloud.google.com/certificate-manager/docs)
- [DNS Configuration Guide](https://cloud.google.com/dns/docs)