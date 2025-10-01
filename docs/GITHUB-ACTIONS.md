# 🚀 AIAlchemy GitHub Actions Workflows

This directory contains automated deployment workflows for the AIAlchemy project on Google Cloud Platform.

## 📋 Available Workflows

### 1. 🚀 Deploy AIAlchemy to GCP (`deploy.yml`)

**Main deployment workflow** that builds and deploys the complete application stack.

**Triggers:**
- Automatic on push to `main` branch
- Manual trigger with gateway options

**Features:**
- Deploys backend, frontend, and optional gateway
- Supports multiple gateway types (nginx, load-balancer, none)
- Configurable domain for load balancer
- Comprehensive deployment summary

**Manual Trigger Options:**
```yaml
gateway_type: nginx | load-balancer | none (default: nginx)
domain_name: your-domain.com (required for load-balancer)
```

### 2. 🌐 Deploy Gateway Only (`deploy-gateway.yml`)

**Gateway-specific deployment** for updating or switching gateway configurations.

**Triggers:**
- Manual trigger only

**Features:**
- Updates gateway without redeploying backend/frontend
- Validates existing services before deployment
- Force rebuild option for container images
- Switch between nginx and load-balancer gateways

**Manual Trigger Options:**
```yaml
gateway_type: nginx | load-balancer (required)
domain_name: your-domain.com (required for load-balancer)
force_rebuild: true | false (default: false)
```

## ⚙️ Configuration

### Required Secrets

Set these secrets in your GitHub repository:

| Secret | Description | Required For |
|--------|-------------|--------------|
| `GCP_PROJECT_ID` | Google Cloud Project ID | All deployments |
| `GCP_SA_KEY` | Service Account JSON key | All deployments |
| `DOMAIN_NAME` | Your domain name | Load Balancer (optional) |

### Service Account Permissions

The service account (`GCP_SA_KEY`) needs these roles:
- `Cloud Run Admin`
- `Artifact Registry Admin`
- `Compute Admin` (for load balancer)
- `Certificate Manager Admin` (for load balancer)
- `Service Usage Admin`

## 🌐 Gateway Deployment Options

### Option 1: NGINX Gateway (Recommended for Development)

```bash
# Automatic deployment (push to main)
git push origin main

# Manual deployment with NGINX gateway
# Go to Actions → Deploy AIAlchemy to GCP → Run workflow
# gateway_type: nginx
```

**Result:**
- Single Cloud Run service acting as reverse proxy
- Routes `/` to frontend, `/api/*` to backend
- Built-in rate limiting and security headers
- Cost-effective for small to medium traffic

### Option 2: Cloud Load Balancer (Recommended for Production)

```bash
# Manual deployment with Load Balancer
# Go to Actions → Deploy AIAlchemy to GCP → Run workflow
# gateway_type: load-balancer
# domain_name: yourdomain.com
```

**Result:**
- Google-managed global load balancer
- Automatic SSL certificate provisioning
- Global CDN and better performance
- Requires DNS configuration

### Option 3: No Gateway (Direct Access)

```bash
# Manual deployment without gateway
# Go to Actions → Deploy AIAlchemy to GCP → Run workflow
# gateway_type: none
```

**Result:**
- Direct access to individual Cloud Run services
- Separate URLs for frontend and backend
- No unified endpoint

## 🔄 Deployment Workflows

### Full Application Deployment

1. **Push to main branch** or **manually trigger** the main workflow
2. Workflow builds and pushes Docker images
3. Deploys backend and frontend services
4. Optionally deploys gateway based on configuration
5. Provides deployment summary with access URLs

### Gateway-Only Updates

1. **Manually trigger** the gateway deployment workflow
2. Validates existing backend/frontend services
3. Deploys or updates gateway configuration
4. Switches between gateway types if needed

## 📊 Deployment Outputs

Both workflows provide comprehensive summaries:

### NGINX Gateway Output
```
🎉 AIAlchemy Deployment Complete!

🚀 Deployed Services
| Service | URL |
|---------|-----|
| 🔧 Backend | https://aialchemy-backend-xxx.a.run.app |
| 🎨 Frontend | https://aialchemy-frontend-xxx.a.run.app |
| 🌐 Gateway | https://aialchemy-gateway-xxx.a.run.app |

🔀 Gateway Access (Recommended)
- Frontend: https://aialchemy-gateway-xxx.a.run.app
- API: https://aialchemy-gateway-xxx.a.run.app/api/
- Docs: https://aialchemy-gateway-xxx.a.run.app/docs
```

### Load Balancer Output
```
🎉 AIAlchemy Deployment Complete!

🌐 Load Balancer
- Domain: https://yourdomain.com
- External IP: 34.102.136.180
- Frontend: https://yourdomain.com
- API: https://yourdomain.com/api/
- Docs: https://yourdomain.com/docs

📋 DNS Configuration Required
Create an A record for 'yourdomain.com' pointing to 34.102.136.180
```

## 🛠️ Local Testing Before Deployment

Test configurations locally before deploying:

```bash
# Test NGINX gateway locally
./test-gateway-local.sh

# Test deployment scripts
GATEWAY_TYPE=nginx ./deploy-gcp-with-gateway.sh
```

## 🔧 Customization

### Modify Gateway Configuration

1. **NGINX Gateway**: Edit `gateway/nginx.conf`
2. **Load Balancer**: Modify `gateway/load-balancer-setup.sh`
3. **Deployment**: Update workflow environment variables

### Add New Workflows

Create new `.yml` files in this directory following the existing patterns:

```yaml
name: Your Workflow Name
on:
  workflow_dispatch:
    inputs:
      # your inputs
env:
  # your environment variables
jobs:
  # your jobs
```

## 🚨 Troubleshooting

### Common Issues

1. **Service Account Permissions**: Ensure all required roles are assigned
2. **Domain Configuration**: Verify DNS settings for load balancer
3. **Image Build Failures**: Check Dockerfile configurations
4. **Deployment Timeouts**: Increase timeout values in workflows

### Debug Commands

```bash
# Check service status
gcloud run services list --region=us-central1

# View logs
gcloud logs tail 'resource.type=cloud_run_revision'

# Check load balancer
gcloud compute url-maps list
gcloud compute ssl-certificates list

# Validate gateway
curl https://your-gateway-url/health
```

### Workflow Debugging

- Check workflow logs in GitHub Actions tab
- Verify secrets are properly set
- Ensure service account has required permissions
- Validate Docker image builds succeed

## 📚 Additional Resources

- [Main Gateway Setup Guide](../../docs/GATEWAY-SETUP.md)
- [Gateway Configuration](../../gateway/README.md)
- [GCP Deployment Guide](../../docs/GCP-DEPLOYMENT.md)

For support, check the troubleshooting sections or create an issue in the repository.