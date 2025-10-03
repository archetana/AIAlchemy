# 🔄 Migration: From Cloud Load Balancer to Nginx Gateway

## 📊 **What Changed**

We replaced the expensive Google Cloud Load Balancer with a cost-effective Nginx gateway running on Cloud Run.

### **Before (Load Balancer):**
- **Cost**: ~$25-40/month fixed fees
- **Components**: Load balancer + SSL cert + forwarding rules + backend services + NEGs
- **Complexity**: 8+ GCP resources to manage

### **After (Nginx Gateway):**
- **Cost**: ~$5-15/month (pay-per-use only)
- **Components**: Single nginx Cloud Run service
- **Complexity**: 1 service + configuration file

## 🎯 **Cost Savings: ~$20-30/month**

## 📁 **New Files Added**

### **1. Nginx Gateway Directory:**
```
nginx-gateway/
├── nginx.conf          # Nginx proxy configuration
├── Dockerfile          # Container definition
└── setup-nginx.sh     # Runtime configuration script
```

### **2. Deployment Scripts:**
```
deploy-nginx-gateway.sh     # Local deployment script
.github/workflows/deploy-nginx.yml  # GitHub Actions workflow
```

### **3. Documentation:**
```
NGINX_GATEWAY_MIGRATION.md  # This file
```

## 🚀 **New Deployment Options**

### **Option 1: Use New Nginx Workflow (Recommended)**
The new workflow `deploy-nginx.yml` replaces the load balancer with nginx gateway.

### **Option 2: Local Deployment**
```bash
./deploy-nginx-gateway.sh
```

### **Option 3: Keep Load Balancer**
The original `deploy.yml` workflow still exists for those who want load balancer.

## ⚙️ **Changes to deploy.yml**

### **What You Need to Update:**

#### **Option A: Switch to Nginx Workflow (Recommended)**
1. **Rename workflows**:
   ```bash
   # Rename original workflow (backup)
   mv .github/workflows/deploy.yml .github/workflows/deploy-loadbalancer.yml
   
   # Make nginx workflow the main one
   mv .github/workflows/deploy-nginx.yml .github/workflows/deploy.yml
   ```

#### **Option B: Modify Existing Workflow**
Update your current `deploy.yml` to remove load balancer steps:

1. **Remove these sections** from `.github/workflows/deploy.yml`:
   ```yaml
   # DELETE these input parameters:
   deploy_gateway:
     description: 'Deploy/Update Cloud Load Balancer Gateway'
   domain_name:
     description: 'Domain name (required for gateway)'
   
   # DELETE these environment variables:
   DEPLOY_GATEWAY: ${{ github.event.inputs.deploy_gateway != 'false' }}
   DOMAIN_NAME: ${{ github.event.inputs.domain_name || secrets.DOMAIN_NAME }}
   
   # DELETE entire step:
   - name: 🌐 Setup Cloud Load Balancer Gateway
   
   # DELETE load balancer references in summary steps
   ```

2. **Add nginx gateway deployment** to your workflow:
   ```yaml
   - name: 🌐 Deploy Nginx Gateway
     run: |
       # Get service URLs
       BACKEND_URL=$(gcloud run services describe aialchemy-backend --region=$REGION --format='value(status.url)')
       FRONTEND_URL=$(gcloud run services describe aialchemy-frontend --region=$REGION --format='value(status.url)')
       BACKEND_HOST=$(echo $BACKEND_URL | sed 's|https://||')
       FRONTEND_HOST=$(echo $FRONTEND_URL | sed 's|https://||')
       
       # Deploy nginx gateway
       cd nginx-gateway
       docker build -t us-central1-docker.pkg.dev/$PROJECT_ID/aialchemy-repo/gateway:$GITHUB_SHA .
       docker push us-central1-docker.pkg.dev/$PROJECT_ID/aialchemy-repo/gateway:$GITHUB_SHA
       
       gcloud run deploy aialchemy-gateway \
         --image=us-central1-docker.pkg.dev/$PROJECT_ID/aialchemy-repo/gateway:$GITHUB_SHA \
         --region=$REGION \
         --set-env-vars="BACKEND_HOST=$BACKEND_HOST,FRONTEND_HOST=$FRONTEND_HOST" \
         --memory=256Mi --cpu=1 --min-instances=1 --max-instances=3 \
         --port=8080 --allow-unauthenticated
   ```

## 🔧 **Frontend Configuration Change**

Update frontend environment variable:
```yaml
# OLD (for load balancer):
--set-env-vars="REACT_APP_API_BASE_URL=$BACKEND_URL,REACT_APP_ENVIRONMENT=production"

# NEW (for nginx gateway):
--set-env-vars="REACT_APP_API_BASE_URL=/api,REACT_APP_ENVIRONMENT=production"
```

This allows the frontend to use relative URLs through the nginx gateway.

## 🗑️ **Cleanup Old Load Balancer Resources**

If you have existing load balancer resources, clean them up:

```bash
# Delete load balancer components (if they exist)
gcloud compute forwarding-rules delete aialchemy-http-rule --global --quiet || true
gcloud compute target-http-proxies delete aialchemy-http-proxy --quiet || true
gcloud compute url-maps delete aialchemy-url-map --global --quiet || true
gcloud compute backend-services delete aialchemy-api-backend --global --quiet || true
gcloud compute backend-services delete aialchemy-frontend-backend --global --quiet || true
gcloud compute network-endpoint-groups delete backend-neg --region=us-central1 --quiet || true
gcloud compute network-endpoint-groups delete frontend-neg --region=us-central1 --quiet || true

# Delete SSL certificate (if using custom domain)
gcloud compute ssl-certificates delete aialchemy-ssl-cert --global --quiet || true
```

## 📋 **Migration Steps**

1. **Commit new nginx gateway files** (already done)
2. **Choose your deployment approach**:
   - Use new nginx workflow, OR
   - Update existing workflow
3. **Deploy using new method**
4. **Test nginx gateway endpoints**
5. **Clean up old load balancer resources**
6. **Update documentation/README**

## 🎯 **Testing the Migration**

After deployment, test these endpoints:
```bash
# Get gateway URL
GATEWAY_URL=$(gcloud run services describe aialchemy-gateway --region=us-central1 --format='value(status.url)')

# Test endpoints
curl -I $GATEWAY_URL/                    # Frontend
curl -I $GATEWAY_URL/api/               # Backend API  
curl -I $GATEWAY_URL/docs               # API docs
curl -I $GATEWAY_URL/health             # Health check
curl -I $GATEWAY_URL/gateway/health     # Gateway health
```

## ✅ **Benefits of Migration**

- **💰 Cost Reduction**: ~$25/month savings
- **🚀 Simplicity**: Single service instead of 8+ resources
- **⚡ Performance**: Direct proxy without extra hops
- **🔧 Control**: Full nginx configuration control
- **📊 Monitoring**: Standard Cloud Run monitoring

## 🔄 **Rollback Plan**

If you need to rollback to load balancer:
1. Use the backup workflow: `deploy-loadbalancer.yml`
2. Set `DOMAIN_NAME` secret in GitHub
3. Run the original deployment

The nginx gateway approach is simpler, cheaper, and easier to maintain! 🚀