# AIAlchemy Gateway Setup Guide

This guide provides two gateway solutions to expose your frontend and backend through a single DNS endpoint on Google Cloud Run.

## 📋 Overview

Both solutions route traffic as follows:
- `yourgateway.com/` → Frontend (React App)
- `yourgateway.com/api/` → Backend (FastAPI)
- `yourgateway.com/docs` → API Documentation

## 🚀 Quick Start

### Option 1: NGINX Gateway (Recommended for Simple Setups)

```bash
# Deploy with NGINX gateway
GATEWAY_TYPE=nginx ./deploy-gcp-with-gateway.sh
```

### Option 2: Cloud Load Balancer (Recommended for Production)

```bash
# Deploy with Cloud Load Balancer (requires domain)
DOMAIN_NAME=yourdomain.com GATEWAY_TYPE=load-balancer ./deploy-gcp-with-gateway.sh
```

## 🏗️ Architecture Comparison

### NGINX Gateway Architecture
```
Internet → Cloud Run (NGINX) → Cloud Run (Frontend/Backend)
```
**Pros:**
- Simple setup and management
- Single Cloud Run service
- Built-in rate limiting and caching
- Cost-effective for small to medium traffic

**Cons:**
- Additional hop for requests
- Limited to single region
- Manual SSL certificate management

### Cloud Load Balancer Architecture
```
Internet → Global Load Balancer → Cloud Run (Frontend/Backend)
```
**Pros:**
- Google-managed infrastructure
- Global CDN and SSL certificates
- Better performance and reliability
- Multi-region support
- Automatic SSL certificate provisioning

**Cons:**
- More complex setup
- Higher cost for low traffic
- Requires domain ownership

## 📖 Detailed Setup Instructions

### NGINX Gateway Setup

#### 1. Deploy the Gateway
```bash
cd /home/agenticai/webapp
GATEWAY_TYPE=nginx ./deploy-gcp-with-gateway.sh
```

#### 2. Access Your Application
After deployment, you'll receive a Cloud Run URL like:
```
https://aialchemy-gateway-xxx-uc.a.run.app
```

Routes:
- **Frontend:** `https://aialchemy-gateway-xxx-uc.a.run.app/`
- **API:** `https://aialchemy-gateway-xxx-uc.a.run.app/api/`
- **Docs:** `https://aialchemy-gateway-xxx-uc.a.run.app/docs`

#### 3. Custom Domain (Optional)
To use a custom domain with the NGINX gateway:

1. **Map domain to Cloud Run:**
```bash
gcloud run domain-mappings create \
    --service=aialchemy-gateway \
    --domain=yourdomain.com \
    --region=us-central1
```

2. **Configure DNS:**
Create a CNAME record pointing to the Cloud Run URL.

### Cloud Load Balancer Setup

#### 1. Prerequisites
- Own a domain name
- Domain DNS management access

#### 2. Deploy with Load Balancer
```bash
cd /home/agenticai/webapp
DOMAIN_NAME=yourdomain.com GATEWAY_TYPE=load-balancer ./deploy-gcp-with-gateway.sh
```

#### 3. Configure DNS
The script will provide an external IP address. Create an A record:

```
Type: A
Name: @ (or your subdomain)
Value: [External IP from script output]
TTL: 300
```

#### 4. Wait for SSL Certificate
Google will automatically provision an SSL certificate. This can take 15-60 minutes.

Check certificate status:
```bash
gcloud compute ssl-certificates list
```

## 🔧 Configuration

### Environment Variables

For NGINX Gateway:
- `BACKEND_URL`: Backend service URL (auto-detected)
- `FRONTEND_URL`: Frontend service URL (auto-detected)

For Load Balancer:
- `DOMAIN_NAME`: Your custom domain (required)

### Nginx Configuration

The NGINX gateway includes:
- **Rate limiting:** API (10 req/s), General (30 req/s)
- **Caching:** Static assets (1 year), API responses (no-cache)
- **Security headers:** HSTS, XSS protection, content type sniffing protection
- **CORS:** Configured for API routes
- **Health checks:** `/health` for gateway, `/api/health` for backend

### Load Balancer Configuration

- **SSL:** Automatic certificate provisioning and renewal
- **CDN:** Enabled for static content
- **Routing:** URL-based routing to appropriate services
- **Health checks:** Automatic service health monitoring

## 🚀 Deployment Commands

### Deploy All Services
```bash
# NGINX Gateway
./deploy-gcp-with-gateway.sh

# Load Balancer Gateway
DOMAIN_NAME=yourdomain.com GATEWAY_TYPE=load-balancer ./deploy-gcp-with-gateway.sh
```

### Deploy Individual Components
```bash
# Backend only
cd backend && gcloud run deploy aialchemy-backend --source .

# Frontend only  
cd frontend && gcloud run deploy aialchemy-frontend --source .

# NGINX Gateway only
cd gateway && ./deploy-nginx-gateway.sh

# Load Balancer only (after services are deployed)
DOMAIN_NAME=yourdomain.com ./gateway/load-balancer-setup.sh
```

## 📊 Monitoring and Management

### View Services
```bash
gcloud run services list
gcloud compute url-maps list  # For load balancer
```

### View Logs
```bash
# All services
gcloud logs tail 'resource.type=cloud_run_revision'

# Specific service
gcloud logs tail 'resource.type=cloud_run_revision AND resource.labels.service_name=aialchemy-gateway'
```

### Health Checks
```bash
# Gateway health
curl https://your-gateway-url/health

# Backend health (through gateway)
curl https://your-gateway-url/api/health

# Direct backend health
curl https://backend-url/health
```

## 🔄 Updates and Maintenance

### Update Services
```bash
# Update backend
cd backend && gcloud run deploy aialchemy-backend --source .

# Update frontend
cd frontend && gcloud run deploy aialchemy-frontend --source .

# Update NGINX gateway
cd gateway && gcloud run deploy aialchemy-gateway --source .
```

### Update Load Balancer Routing
```bash
# Edit routing rules
vim /tmp/url-map.yaml
gcloud compute url-maps import aialchemy-gateway-url-map --source=/tmp/url-map.yaml --global
```

## 🛠️ Troubleshooting

### Common Issues

1. **502 Bad Gateway (NGINX)**
   - Check backend/frontend service URLs
   - Verify services are running: `gcloud run services list`
   - Check logs: `gcloud logs tail`

2. **SSL Certificate Pending (Load Balancer)**
   - Verify DNS A record is configured correctly
   - Wait 15-60 minutes for certificate provisioning
   - Check: `gcloud compute ssl-certificates describe aialchemy-gateway-ssl-cert`

3. **CORS Issues**
   - Ensure API routes use `/api/` prefix
   - Check NGINX CORS headers configuration
   - Verify frontend is making requests to correct URLs

### Debug Commands
```bash
# Test gateway connectivity
curl -v https://your-gateway-url/health

# Check service connectivity
gcloud run services describe aialchemy-backend --region=us-central1

# View detailed logs
gcloud logs read 'resource.type=cloud_run_revision' --limit 50
```

## 💰 Cost Considerations

### NGINX Gateway
- 1 additional Cloud Run instance
- ~$5-15/month for low traffic
- Scales with usage

### Cloud Load Balancer
- Global Load Balancer: ~$18/month base cost
- SSL Certificate: Free (Google-managed)
- CDN and traffic costs additional
- More cost-effective for high traffic

## 🔐 Security Features

Both solutions include:
- **HTTPS/TLS encryption**
- **Security headers** (HSTS, XSS protection, etc.)
- **Rate limiting** (NGINX only)
- **CORS configuration**
- **Input validation**

Additional for Load Balancer:
- **DDoS protection**
- **Google Cloud Armor integration**
- **Geographic restrictions**

## 📚 Next Steps

1. **Monitor Performance:** Set up Cloud Monitoring alerts
2. **Configure Logging:** Enable structured logging
3. **Set up CI/CD:** Automate deployments with GitHub Actions
4. **Scale Configuration:** Adjust CPU/memory based on traffic
5. **Security Hardening:** Configure Cloud Armor rules (Load Balancer)

For support, check the troubleshooting section or create an issue in the repository.