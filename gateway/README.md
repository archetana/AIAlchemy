# AIAlchemy Cloud Load Balancer Gateway

This directory contains the Cloud Load Balancer configuration for routing traffic between the frontend and backend services through a single domain endpoint.

## 🌐 Gateway Solution

**Cloud Load Balancer** - Google-managed global load balancer with SSL certificates and CDN.

**Files:**
- `load-balancer-setup.sh` - Setup script for load balancer configuration

**Features:**
- Global CDN for improved performance
- Automatic SSL certificate provisioning and renewal
- DDoS protection and security
- Multi-region support
- Google-managed infrastructure
- URL-based routing

## 🚀 Quick Deploy

### Via GitHub Actions (Recommended)
1. Go to **Actions** tab → **"Deploy AIAlchemy to GCP"**
2. Click **"Run workflow"**
3. Set options:
   - `deploy_gateway: true`
   - `domain_name: yourdomain.com`
   - `gateway_only: false` (for full deployment)
4. Click **"Run workflow"**

### Via Script
```bash
# From project root (requires domain)
DOMAIN_NAME=yourdomain.com ./deploy-gcp-with-gateway.sh

# Or setup just the load balancer
DOMAIN_NAME=yourdomain.com ./gateway/load-balancer-setup.sh
```

## 🔀 Traffic Routing

The load balancer routes traffic as follows:

| Path | Destination | Description |
|------|-------------|-------------|
| `/` | Frontend | React application |
| `/api/*` | Backend | API endpoints |
| `/docs` | Backend | FastAPI documentation |
| `/redoc` | Backend | Alternative API documentation |
| `/openapi.json` | Backend | OpenAPI specification |

## 🔧 Configuration

### Domain Configuration

- `DOMAIN_NAME` - Your custom domain (e.g., `aialchemy.com`)
- Set as GitHub secret or provide during manual deployment

### DNS Configuration Required

After deployment, you'll receive an external IP address. Create an A record:

```
Type: A
Name: @ (or your subdomain)
Value: [External IP from deployment output]
TTL: 300
```

## 📊 Monitoring

### Health Checks
```bash
# Backend health through gateway
curl https://yourdomain.com/api/health

# Frontend availability
curl https://yourdomain.com
```

### Logs
```bash
# Load Balancer logs
gcloud logs tail 'resource.type=http_load_balancer'

# Backend logs
gcloud logs tail 'resource.type=cloud_run_revision AND resource.labels.service_name=aialchemy-backend'

# Frontend logs  
gcloud logs tail 'resource.type=cloud_run_revision AND resource.labels.service_name=aialchemy-frontend'
```

## 🛠️ Management

### View Load Balancer Status
```bash
# List URL maps
gcloud compute url-maps list

# Check SSL certificates
gcloud compute ssl-certificates list

# View forwarding rules
gcloud compute forwarding-rules list --global
```

### Update Load Balancer Routing

Edit the URL map in `load-balancer-setup.sh` and run:
```bash
gcloud compute url-maps import aialchemy-gateway-url-map --source=/tmp/url-map.yaml --global
```

## 🔐 Security Features

- **SSL/TLS termination** with automatic certificate management
- **DDoS protection** via Google Cloud infrastructure
- **Google Cloud Armor** integration available
- **Geographic restrictions** (configurable)
- **Request routing** based on URL patterns
- **Backend service health checks**

## ⏱️ SSL Certificate Provisioning

- **Automatic provisioning** after DNS configuration
- **Typical time:** 15-60 minutes after DNS propagation
- **Automatic renewal** handled by Google
- **Wildcard certificates** supported

## 💰 Cost Considerations

- **Base cost:** ~$18/month for global load balancer
- **SSL certificates:** Free (Google-managed)
- **CDN and traffic:** Additional usage-based costs
- **More cost-effective** for high traffic compared to container-based solutions

## 🔄 Deployment Options

### Full Deployment
Deploy backend, frontend, and gateway:
```bash
# GitHub Actions
deploy_gateway: true
gateway_only: false
domain_name: yourdomain.com
```

### Gateway-Only Update
Update just the gateway configuration:
```bash
# GitHub Actions  
deploy_gateway: true
gateway_only: true
domain_name: yourdomain.com
```

### No Gateway
Deploy services without gateway:
```bash
# GitHub Actions
deploy_gateway: false
```

## 🎯 Production Ready

This solution is production-ready and includes:
- ✅ Enterprise-grade infrastructure
- ✅ Automatic scaling and load distribution
- ✅ Global CDN for performance
- ✅ Managed SSL certificates
- ✅ DDoS protection
- ✅ Health monitoring
- ✅ Automated deployment via GitHub Actions

For detailed setup instructions, see [GATEWAY-SETUP.md](../docs/GATEWAY-SETUP.md).