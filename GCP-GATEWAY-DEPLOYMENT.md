# AIAlchemy GCP Deployment with API Gateway

## 🏗️ Architecture Overview

This deployment creates a robust, production-ready architecture on Google Cloud Platform with API Gateway routing:

```
┌─────────────────────────────────────────────────────────────┐
│                    API Gateway                              │
│              (aialchemy-gateway)                            │
│                                                             │
│  https://aialchemy-gateway-xxx.uc.gateway.dev              │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ├─── /api/** ──────────────────────┐
                      │                                   │
                      ├─── /health ──────────────────────┤
                      │                                   │
                      └─── /** ──────────────────────────┤
                                                          │
                                                          ▼
                     ┌──────────────────────────────────────┐
                     │         Backend Service              │
                     │      (aialchemy-backend)             │
                     │                                      │
                     │  Cloud Run - FastAPI Backend        │
                     │  - Private (no direct access)       │
                     │  - Auto-scaling                      │
                     │  - Health checks                     │
                     └──────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                 Frontend Service                            │
│              (aialchemy-frontend)                           │
│                                                             │
│  https://aialchemy-frontend-xxx.run.app                    │
│  - React SPA                                                │
│  - Environment-aware API detection                         │
│  - Automatically uses Gateway URL                          │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Automated GitHub Actions Deployment

### Prerequisites

1. **GCP Project Setup**:
   ```bash
   # Create project
   gcloud projects create YOUR_PROJECT_ID --name="AIAlchemy Production"
   
   # Set billing account
   gcloud billing accounts link YOUR_PROJECT_ID --billing-account=YOUR_BILLING_ACCOUNT
   ```

2. **Service Account Creation**:
   ```bash
   # Create service account
   gcloud iam service-accounts create aialchemy-deployer \
     --description="AIAlchemy GitHub Actions deployment" \
     --display-name="AIAlchemy Deployer"
   
   # Grant necessary permissions
   gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
     --member="serviceAccount:aialchemy-deployer@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
     --role="roles/run.admin"
   
   gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
     --member="serviceAccount:aialchemy-deployer@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
     --role="roles/apigateway.admin"
   
   gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
     --member="serviceAccount:aialchemy-deployer@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
     --role="roles/servicemanagement.admin"
   
   gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
     --member="serviceAccount:aialchemy-deployer@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
     --role="roles/artifactregistry.admin"
   
   # Create and download key
   gcloud iam service-accounts keys create key.json \
     --iam-account=aialchemy-deployer@YOUR_PROJECT_ID.iam.gserviceaccount.com
   ```

3. **GitHub Secrets Configuration**:
   
   Add these secrets to your GitHub repository:
   
   - `GCP_PROJECT_ID`: Your GCP project ID
   - `GCP_SA_KEY`: Content of the service account key.json file

### Repository Secrets Setup

Navigate to your GitHub repository → Settings → Secrets and variables → Actions:

```
GCP_PROJECT_ID = your-gcp-project-id
GCP_SA_KEY = {
  "type": "service_account",
  "project_id": "your-project-id",
  ...
}
```

## 🔧 How the Deployment Works

### 1. Infrastructure Setup Job

The deployment creates:

1. **Artifact Registry Repository** for container images
2. **Backend Cloud Run Service** (private, no direct access)  
3. **API Gateway Configuration** with OpenAPI specification
4. **API Gateway** that routes traffic to backend

### 2. Frontend Deployment Job

1. **Environment-Aware Configuration**: Frontend automatically detects its environment
2. **Dynamic API URLs**: No hardcoded API endpoints
3. **Production Optimization**: Built with production environment variables

## 🌐 Environment-Aware Frontend Configuration

The frontend automatically detects its environment and configures API URLs:

### Development Environments
- **Local**: `http://localhost:8000`
- **GitPod**: Uses GitPod's port forwarding
- **Codespaces**: Uses Codespaces port mapping

### Production Environment
- **GCP Production**: Uses current domain (routed through API Gateway)

### Configuration File: `/frontend/src/config/api.js`

```javascript
const getApiBaseUrl = () => {
  // Production: Use same domain (Gateway routes to backend)
  if (window.location.hostname !== 'localhost' && !isDevEnvironment) {
    return `${window.location.protocol}//${window.location.host}`;
  }
  
  // Development: Use localhost backend
  return 'http://localhost:8000';
};
```

## 📋 Manual Deployment Steps

If you need to deploy manually:

```bash
# 1. Clone and prepare
git clone YOUR_REPO_URL
cd AIAlchemy

# 2. Set project
export PROJECT_ID=your-project-id
gcloud config set project $PROJECT_ID

# 3. Build and deploy backend
cd backend
gcloud run deploy aialchemy-backend \
  --source . \
  --region us-central1 \
  --no-allow-unauthenticated

# 4. Create API Gateway configuration
cat > api-config.yaml << 'EOF'
swagger: '2.0'
info:
  title: AIAlchemy API Gateway
  version: 1.0.0
paths:
  /api/**:
    x-google-backend:
      address: BACKEND_URL_HERE
EOF

# Replace BACKEND_URL_HERE with actual backend URL
BACKEND_URL=$(gcloud run services describe aialchemy-backend --region=us-central1 --format='value(status.url)')
sed -i "s|BACKEND_URL_HERE|$BACKEND_URL|g" api-config.yaml

# 5. Deploy API Gateway
gcloud api-gateway apis create aialchemy-api --project=$PROJECT_ID
gcloud api-gateway api-configs create aialchemy-config \
  --api=aialchemy-api \
  --openapi-spec=api-config.yaml

gcloud api-gateway gateways create aialchemy-gateway \
  --api=aialchemy-api \
  --api-config=aialchemy-config \
  --location=us-central1

# 6. Deploy frontend
cd ../frontend
GATEWAY_URL=$(gcloud api-gateway gateways describe aialchemy-gateway --location=us-central1 --format='value(defaultHostname)')

cat > .env.production << EOF
REACT_APP_API_URL=https://$GATEWAY_URL
REACT_APP_ENVIRONMENT=production
EOF

gcloud run deploy aialchemy-frontend \
  --source . \
  --region us-central1 \
  --allow-unauthenticated
```

## 🔒 Security Features

### API Gateway Security
- **Rate Limiting**: Built-in DDoS protection
- **Authentication**: Can be configured for API keys/OAuth
- **SSL Termination**: Automatic HTTPS with Google-managed certificates
- **Backend Protection**: Backend services are not publicly accessible

### Cloud Run Security
- **Private Services**: Backend only accessible through Gateway
- **IAM Integration**: Fine-grained access controls
- **Container Security**: Automatic security scanning
- **VPC Integration**: Can be configured for private networking

## 📊 Monitoring and Observability

### Built-in Monitoring
```bash
# View logs
gcloud logs tail "resource.type=cloud_run_revision"

# Monitor API Gateway
gcloud logging read 'resource.type="api_gateway"'

# Check service status
gcloud run services list
gcloud api-gateway gateways list
```

### Health Checks
- **Backend Health**: `GET /health`
- **API Status**: `GET /api/status`
- **Gateway Health**: Automatic Google monitoring

## 🚀 Deployment Triggers

### Automatic Deployment
- **Push to `main`**: Triggers full deployment
- **Manual Trigger**: Via GitHub Actions UI

### Manual Trigger Options
```yaml
workflow_dispatch:
  inputs:
    environment:
      description: 'Deployment environment'
      required: true
      default: 'production'
      type: choice
      options:
        - production
        - staging
```

## 📈 Scaling and Performance

### Auto-Scaling Configuration
- **Backend**: 1-10 instances based on traffic
- **Frontend**: 1-5 instances for static content serving
- **Gateway**: Managed by Google (unlimited scale)

### Performance Optimizations
- **Container Optimization**: Multi-stage Docker builds
- **CDN Integration**: Can be configured with Cloud CDN
- **Connection Pooling**: Built into Cloud Run
- **Automatic SSL**: Google-managed certificates

## 🔄 CI/CD Pipeline

The GitHub Actions workflow includes:

1. **Code Checkout** and authentication
2. **Infrastructure Provisioning** (APIs, repositories)
3. **Container Building** and pushing to Artifact Registry
4. **Backend Deployment** (private Cloud Run service)
5. **API Gateway Setup** with OpenAPI configuration
6. **Frontend Configuration** with environment detection
7. **Frontend Deployment** with dynamic API URLs

## 🛠️ Troubleshooting

### Common Issues

1. **API Gateway Not Routing**:
   ```bash
   # Check gateway status
   gcloud api-gateway gateways describe aialchemy-gateway --location=us-central1
   
   # Verify API config
   gcloud api-gateway api-configs describe aialchemy-config --api=aialchemy-api
   ```

2. **Frontend Cannot Connect to API**:
   - Check browser console for API configuration logs
   - Verify environment detection: `apiUtils.testEnvironment()`
   - Ensure Gateway URL is accessible

3. **Backend Service Down**:
   ```bash
   # Check backend logs
   gcloud logs tail "resource.type=cloud_run_revision AND resource.labels.service_name=aialchemy-backend"
   
   # Verify backend service
   gcloud run services describe aialchemy-backend --region=us-central1
   ```

### Debug Commands
```bash
# Test API connectivity
curl -v https://your-gateway-url/health

# Check frontend configuration
# In browser console:
window.apiUtils.getApiConfig()
window.apiUtils.testEnvironment()
```

## 💰 Cost Optimization

### Pay-per-Use Model
- **Cloud Run**: Only pay for requests and compute time
- **API Gateway**: Pay per API call
- **Artifact Registry**: Pay for storage of container images

### Cost-Saving Tips
- Configure appropriate instance limits
- Use Cloud Run's concurrency settings
- Enable Cloud CDN for static assets
- Monitor usage with Cloud Billing alerts

## 🔐 Production Checklist

Before going live:

- [ ] Configure custom domain for API Gateway
- [ ] Set up SSL certificates
- [ ] Configure authentication/authorization
- [ ] Set up monitoring alerts
- [ ] Configure backup strategies
- [ ] Enable audit logging
- [ ] Review security policies
- [ ] Set up error reporting
- [ ] Configure rate limiting
- [ ] Test disaster recovery

This deployment architecture provides a scalable, secure, and maintainable solution for the AIAlchemy platform on Google Cloud Platform.