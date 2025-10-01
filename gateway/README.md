# AIAlchemy Gateway

This directory contains the gateway configuration for routing traffic between the frontend and backend services through a single endpoint.

## 🌐 Gateway Options

### 1. NGINX Gateway (Recommended for Development/Small Scale)

A containerized NGINX reverse proxy deployed as a Cloud Run service.

**Files:**
- `Dockerfile` - NGINX container configuration
- `nginx.conf` - NGINX routing and security configuration  
- `entrypoint.sh` - Dynamic configuration script
- `deploy-nginx-gateway.sh` - Deployment script

**Features:**
- Rate limiting (API: 10 req/s, General: 30 req/s)
- Static asset caching (1 year)
- CORS configuration
- Security headers
- Health checks
- Gzip compression

### 2. Cloud Load Balancer (Recommended for Production)

Google Cloud's global load balancer with SSL certificates and CDN.

**Files:**
- `load-balancer-setup.sh` - Setup script for load balancer configuration

**Features:**
- Global CDN
- Automatic SSL certificate provisioning
- DDoS protection
- Multi-region support
- Google-managed infrastructure

## 🚀 Quick Deploy

### NGINX Gateway
```bash
# From project root
GATEWAY_TYPE=nginx ./deploy-gcp-with-gateway.sh

# Or deploy just the gateway
cd gateway
./deploy-nginx-gateway.sh
```

### Cloud Load Balancer
```bash
# From project root (requires domain)
DOMAIN_NAME=yourdomain.com GATEWAY_TYPE=load-balancer ./deploy-gcp-with-gateway.sh

# Or setup just the load balancer
DOMAIN_NAME=yourdomain.com ./gateway/load-balancer-setup.sh
```

## 🔀 Traffic Routing

Both gateways route traffic as follows:

| Path | Destination | Description |
|------|-------------|-------------|
| `/` | Frontend | React application |
| `/api/*` | Backend | API endpoints (prefix removed) |
| `/docs` | Backend | FastAPI documentation |
| `/redoc` | Backend | Alternative API documentation |
| `/openapi.json` | Backend | OpenAPI specification |
| `/health` | Gateway | Gateway health check |
| `/api/health` | Backend | Backend health check (proxied) |

## 🔧 Configuration

### Environment Variables (NGINX)

- `BACKEND_URL` - Backend Cloud Run service URL
- `FRONTEND_URL` - Frontend Cloud Run service URL

These are automatically set by the deployment scripts.

### Domain Configuration (Load Balancer)

- `DOMAIN_NAME` - Your custom domain (e.g., `aialchemy.com`)

## 📊 Monitoring

### Health Checks
```bash
# Gateway health
curl https://your-gateway-url/health

# Backend health through gateway
curl https://your-gateway-url/api/health
```

### Logs
```bash
# NGINX Gateway logs
gcloud logs tail 'resource.type=cloud_run_revision AND resource.labels.service_name=aialchemy-gateway'

# Load Balancer logs
gcloud logs tail 'resource.type=http_load_balancer'
```

## 🛠️ Customization

### Modify NGINX Configuration

Edit `nginx.conf` to customize:
- Rate limits
- Caching policies
- Security headers
- Routing rules

Then redeploy:
```bash
cd gateway
gcloud run deploy aialchemy-gateway --source .
```

### Modify Load Balancer Routing

Edit the URL map in `load-balancer-setup.sh` and run:
```bash
gcloud compute url-maps import aialchemy-gateway-url-map --source=/tmp/url-map.yaml --global
```

## 🔐 Security

### NGINX Gateway Security
- Rate limiting per IP
- Security headers (HSTS, XSS protection, etc.)
- CORS configuration
- Request size limits
- Deny access to sensitive files

### Load Balancer Security
- Google Cloud Armor integration
- DDoS protection
- SSL/TLS termination
- Geographic restrictions (configurable)

## 💡 Tips

1. **Development:** Use NGINX gateway for simplicity
2. **Production:** Use Cloud Load Balancer for performance and reliability
3. **Custom Domain:** Both options support custom domains
4. **SSL Certificates:** Load Balancer provides automatic SSL; NGINX requires manual setup
5. **Cost:** NGINX is more cost-effective for low traffic; Load Balancer better for high traffic

For detailed setup instructions, see [GATEWAY-SETUP.md](../docs/GATEWAY-SETUP.md).