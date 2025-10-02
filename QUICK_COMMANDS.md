# 🚀 Quick Commands: Google Cloud Load Balancer Setup

## 🎯 One-Command Setup

```bash
# Replace with your actual domain
DOMAIN_NAME=aialchemy.yourdomain.com PROJECT_ID=your-project-id ./setup-load-balancer.sh
```

## 📋 Step-by-Step Commands

### 1. Prerequisites Setup
```bash
# Set environment variables (replace with your values)
export PROJECT_ID="your-project-id"
export REGION="us-central1" 
export DOMAIN_NAME="aialchemy.yourdomain.com"

# Set GCP project
gcloud config set project $PROJECT_ID

# Enable APIs
gcloud services enable compute.googleapis.com run.googleapis.com certificatemanager.googleapis.com
```

### 2. Verify Cloud Run Services
```bash
# List services
gcloud run services list --region=$REGION

# Get service URLs
BACKEND_URL=$(gcloud run services describe aialchemy-backend --region=$REGION --format='value(status.url)')
FRONTEND_URL=$(gcloud run services describe aialchemy-frontend --region=$REGION --format='value(status.url)')
echo "Backend: $BACKEND_URL"
echo "Frontend: $FRONTEND_URL"
```

### 3. Create Network Endpoint Groups
```bash
# Backend NEG
gcloud compute network-endpoint-groups create aialchemy-backend-neg \
    --region=$REGION \
    --network-endpoint-type=serverless \
    --cloud-run-service=aialchemy-backend

# Frontend NEG  
gcloud compute network-endpoint-groups create aialchemy-frontend-neg \
    --region=$REGION \
    --network-endpoint-type=serverless \
    --cloud-run-service=aialchemy-frontend
```

### 4. Create Backend Services
```bash
# API Backend Service
gcloud compute backend-services create aialchemy-api-backend \
    --global --protocol=HTTPS --enable-cdn --cache-mode=USE_ORIGIN_HEADERS

gcloud compute backend-services add-backend aialchemy-api-backend \
    --global --network-endpoint-group=aialchemy-backend-neg \
    --network-endpoint-group-region=$REGION

# Frontend Backend Service
gcloud compute backend-services create aialchemy-frontend-backend \
    --global --protocol=HTTPS --enable-cdn --cache-mode=CACHE_ALL_STATIC

gcloud compute backend-services add-backend aialchemy-frontend-backend \
    --global --network-endpoint-group=aialchemy-frontend-neg \
    --network-endpoint-group-region=$REGION
```

### 5. Create URL Map
```bash
# Create URL map config
cat > /tmp/url-map.yaml << EOF
name: aialchemy-url-map
defaultService: projects/$PROJECT_ID/global/backendServices/aialchemy-frontend-backend
hostRules:
- hosts: ['$DOMAIN_NAME']
  pathMatcher: aialchemy-matcher
pathMatchers:
- name: aialchemy-matcher
  defaultService: projects/$PROJECT_ID/global/backendServices/aialchemy-frontend-backend
  pathRules:
  - paths: ['/api/*', '/docs*', '/redoc*', '/openapi.json', '/health']
    service: projects/$PROJECT_ID/global/backendServices/aialchemy-api-backend
  - paths: ['/*']
    service: projects/$PROJECT_ID/global/backendServices/aialchemy-frontend-backend
EOF

# Import URL map
gcloud compute url-maps import aialchemy-url-map --source=/tmp/url-map.yaml --global
```

### 6. Create SSL Certificate
```bash
# Create managed SSL certificate
gcloud compute ssl-certificates create aialchemy-ssl-cert \
    --domains=$DOMAIN_NAME --global
```

### 7. Create HTTPS Proxy and Forwarding Rule
```bash
# Create HTTPS target proxy
gcloud compute target-https-proxies create aialchemy-https-proxy \
    --ssl-certificates=aialchemy-ssl-cert --url-map=aialchemy-url-map

# Create global forwarding rule  
gcloud compute forwarding-rules create aialchemy-https-rule \
    --global --target-https-proxy=aialchemy-https-proxy --ports=443
```

### 8. Get External IP
```bash
# Get load balancer IP
EXTERNAL_IP=$(gcloud compute forwarding-rules describe aialchemy-https-rule --global --format='value(IPAddress)')
echo "Configure DNS: $DOMAIN_NAME -> $EXTERNAL_IP"
```

## 🔍 Monitoring & Status Commands

### Check SSL Certificate Status
```bash
gcloud compute ssl-certificates describe aialchemy-ssl-cert --global
```

### Check Load Balancer Components
```bash
# List all components
gcloud compute url-maps list
gcloud compute backend-services list  
gcloud compute ssl-certificates list
gcloud compute forwarding-rules list --global
```

### View Logs
```bash
# Load balancer logs
gcloud logs read 'resource.type=http_load_balancer' --limit=20

# Backend service logs
gcloud logs read 'resource.type=cloud_run_revision AND resource.labels.service_name=aialchemy-backend' --limit=10
```

### Test Endpoints
```bash
# Test health
curl -v https://$DOMAIN_NAME/health

# Test API
curl -v https://$DOMAIN_NAME/api/

# Test frontend  
curl -I https://$DOMAIN_NAME/
```

## 🧹 Cleanup Commands

### Remove Load Balancer (if needed)
```bash
# Delete in reverse order
gcloud compute forwarding-rules delete aialchemy-https-rule --global --quiet
gcloud compute target-https-proxies delete aialchemy-https-proxy --quiet
gcloud compute ssl-certificates delete aialchemy-ssl-cert --global --quiet  
gcloud compute url-maps delete aialchemy-url-map --global --quiet
gcloud compute backend-services delete aialchemy-api-backend --global --quiet
gcloud compute backend-services delete aialchemy-frontend-backend --global --quiet
gcloud compute network-endpoint-groups delete aialchemy-backend-neg --region=$REGION --quiet
gcloud compute network-endpoint-groups delete aialchemy-frontend-neg --region=$REGION --quiet
```

## ⚡ DNS Configuration

### Cloudflare DNS
```bash
# Add A record via Cloudflare API
curl -X POST "https://api.cloudflare.com/client/v4/zones/YOUR_ZONE_ID/dns_records" \
  -H "X-Auth-Email: your-email@domain.com" \
  -H "X-Auth-Key: your-api-key" \
  -H "Content-Type: application/json" \
  --data '{"type":"A","name":"aialchemy","content":"'$EXTERNAL_IP'","ttl":300}'
```

### Google Cloud DNS
```bash
# Create managed zone
gcloud dns managed-zones create aialchemy-zone \
    --description="AIAlchemy DNS zone" --dns-name=yourdomain.com.

# Add A record
gcloud dns record-sets transaction start --zone=aialchemy-zone
gcloud dns record-sets transaction add $EXTERNAL_IP \
    --name=$DOMAIN_NAME. --ttl=300 --type=A --zone=aialchemy-zone
gcloud dns record-sets transaction execute --zone=aialchemy-zone
```

## 🚨 Troubleshooting Commands

### Check DNS Propagation
```bash
# Check DNS resolution
nslookup $DOMAIN_NAME
dig $DOMAIN_NAME

# Verify IP matches
RESOLVED_IP=$(dig +short $DOMAIN_NAME)
echo "Expected: $EXTERNAL_IP"
echo "Resolved: $RESOLVED_IP"
```

### Check Backend Health
```bash
gcloud compute backend-services get-health aialchemy-api-backend --global
gcloud compute backend-services get-health aialchemy-frontend-backend --global
```

### Force SSL Certificate Check
```bash
# Re-provision certificate (if stuck)
gcloud compute ssl-certificates delete aialchemy-ssl-cert --global --quiet
gcloud compute ssl-certificates create aialchemy-ssl-cert --domains=$DOMAIN_NAME --global
```