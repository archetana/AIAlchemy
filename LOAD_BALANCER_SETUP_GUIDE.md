# 🌐 Google Cloud Load Balancer Setup Guide

Complete step-by-step guide to configure Google Cloud Load Balancer for AIAlchemy frontend and backend.

## 📋 Prerequisites

Before starting, ensure you have:
- ✅ Google Cloud CLI installed and authenticated
- ✅ A domain name (e.g., `aialchemy.yourdomain.com`)
- ✅ Backend and Frontend already deployed to Cloud Run
- ✅ Proper GCP permissions (Compute Admin, Certificate Manager Admin)

## 🚀 Step 1: Verify Existing Services

First, let's check your current Cloud Run services:

```bash
# Set your project (replace with your actual project ID)
export PROJECT_ID="aialchemy-prod"
export REGION="us-central1"
export DOMAIN_NAME="aialchemy.yourdomain.com"  # Replace with your domain

# Set project
gcloud config set project $PROJECT_ID

# List existing services
gcloud run services list --region=$REGION

# Get service URLs
BACKEND_URL=$(gcloud run services describe aialchemy-backend --region=$REGION --format='value(status.url)' 2>/dev/null || echo "")
FRONTEND_URL=$(gcloud run services describe aialchemy-frontend --region=$REGION --format='value(status.url)' 2>/dev/null || echo "")

echo "Backend URL: $BACKEND_URL"
echo "Frontend URL: $FRONTEND_URL"
```

## 🔧 Step 2: Enable Required APIs

Enable all necessary Google Cloud APIs:

```bash
# Enable required APIs
gcloud services enable compute.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable certificatemanager.googleapis.com
gcloud services enable cloudbuild.googleapis.com

# Verify APIs are enabled
gcloud services list --enabled --filter="name:(compute.googleapis.com OR certificatemanager.googleapis.com OR run.googleapis.com)"
```

## 🔗 Step 3: Create Network Endpoint Groups (NEGs)

NEGs connect the load balancer to your Cloud Run services:

```bash
# Create Backend NEG
gcloud compute network-endpoint-groups create aialchemy-backend-neg \
    --region=$REGION \
    --network-endpoint-type=serverless \
    --cloud-run-service=aialchemy-backend

# Create Frontend NEG
gcloud compute network-endpoint-groups create aialchemy-frontend-neg \
    --region=$REGION \
    --network-endpoint-type=serverless \
    --cloud-run-service=aialchemy-frontend

# Verify NEGs created
gcloud compute network-endpoint-groups list
```

## 🏗️ Step 4: Create Backend Services

Backend services define how traffic is distributed:

```bash
# Create API Backend Service (for /api/* routes)
gcloud compute backend-services create aialchemy-api-backend \
    --global \
    --protocol=HTTPS \
    --enable-cdn \
    --cache-mode=USE_ORIGIN_HEADERS

# Add backend NEG to API service
gcloud compute backend-services add-backend aialchemy-api-backend \
    --global \
    --network-endpoint-group=aialchemy-backend-neg \
    --network-endpoint-group-region=$REGION

# Create Frontend Backend Service (for /* routes)
gcloud compute backend-services create aialchemy-frontend-backend \
    --global \
    --protocol=HTTPS \
    --enable-cdn \
    --cache-mode=CACHE_ALL_STATIC

# Add frontend NEG to frontend service
gcloud compute backend-services add-backend aialchemy-frontend-backend \
    --global \
    --network-endpoint-group=aialchemy-frontend-neg \
    --network-endpoint-group-region=$REGION

# Verify backend services
gcloud compute backend-services list
```

## 🗺️ Step 5: Create URL Map for Traffic Routing

The URL map defines how requests are routed based on paths:

```bash
# Create URL map configuration file
cat > /tmp/url-map.yaml << EOF
name: aialchemy-url-map
defaultService: projects/$PROJECT_ID/global/backendServices/aialchemy-frontend-backend
hostRules:
- hosts:
  - '$DOMAIN_NAME'
  pathMatcher: aialchemy-matcher
pathMatchers:
- name: aialchemy-matcher
  defaultService: projects/$PROJECT_ID/global/backendServices/aialchemy-frontend-backend
  pathRules:
  - paths:
    - /api/*
    - /docs*
    - /redoc*
    - /openapi.json
    - /health
    service: projects/$PROJECT_ID/global/backendServices/aialchemy-api-backend
  - paths:
    - /*
    service: projects/$PROJECT_ID/global/backendServices/aialchemy-frontend-backend
EOF

# Import the URL map
gcloud compute url-maps import aialchemy-url-map \
    --source=/tmp/url-map.yaml \
    --global

# Verify URL map
gcloud compute url-maps describe aialchemy-url-map --global
```

## 🔒 Step 6: Create SSL Certificate

Google manages SSL certificates automatically:

```bash
# Create managed SSL certificate
gcloud compute ssl-certificates create aialchemy-ssl-cert \
    --domains=$DOMAIN_NAME \
    --global

# Check certificate status (will be PROVISIONING initially)
gcloud compute ssl-certificates describe aialchemy-ssl-cert --global
```

## 🔐 Step 7: Create HTTPS Target Proxy

The target proxy terminates SSL and forwards to the URL map:

```bash
# Create HTTPS target proxy
gcloud compute target-https-proxies create aialchemy-https-proxy \
    --ssl-certificates=aialchemy-ssl-cert \
    --url-map=aialchemy-url-map

# Verify proxy creation
gcloud compute target-https-proxies describe aialchemy-https-proxy
```

## 🌍 Step 8: Create Global Forwarding Rule

This creates the external IP and routes traffic to the proxy:

```bash
# Create forwarding rule (this assigns the external IP)
gcloud compute forwarding-rules create aialchemy-https-rule \
    --global \
    --target-https-proxy=aialchemy-https-proxy \
    --ports=443

# Get the external IP address
EXTERNAL_IP=$(gcloud compute forwarding-rules describe aialchemy-https-rule --global --format='value(IPAddress)')
echo "Your Load Balancer External IP: $EXTERNAL_IP"
```

## 📡 Step 9: Configure DNS

Point your domain to the load balancer:

```bash
echo "Configure DNS with these settings:"
echo "=================================="
echo "Record Type: A"
echo "Name: $DOMAIN_NAME"
echo "Value: $EXTERNAL_IP"
echo "TTL: 300 (or your preference)"
echo ""
echo "Example DNS configuration:"
echo "aialchemy.yourdomain.com.  300  IN  A  $EXTERNAL_IP"
```

### DNS Configuration Examples:

**For Cloudflare:**
```bash
# Using Cloudflare API (replace with your credentials)
curl -X POST "https://api.cloudflare.com/client/v4/zones/YOUR_ZONE_ID/dns_records" \
     -H "X-Auth-Email: your-email@domain.com" \
     -H "X-Auth-Key: your-api-key" \
     -H "Content-Type: application/json" \
     --data '{"type":"A","name":"aialchemy","content":"'$EXTERNAL_IP'","ttl":300}'
```

**For Google Cloud DNS:**
```bash
# Create DNS zone (if not exists)
gcloud dns managed-zones create aialchemy-zone \
    --description="AIAlchemy DNS zone" \
    --dns-name=yourdomain.com.

# Add A record
gcloud dns record-sets transaction start --zone=aialchemy-zone
gcloud dns record-sets transaction add $EXTERNAL_IP \
    --name=aialchemy.yourdomain.com. \
    --ttl=300 \
    --type=A \
    --zone=aialchemy-zone
gcloud dns record-sets transaction execute --zone=aialchemy-zone
```

## ⏱️ Step 10: Wait for SSL Certificate Provisioning

SSL certificates take time to provision after DNS is configured:

```bash
# Monitor SSL certificate status
echo "Monitoring SSL certificate provisioning..."
while true; do
    STATUS=$(gcloud compute ssl-certificates describe aialchemy-ssl-cert --global --format='value(managed.status)')
    echo "Certificate status: $STATUS"
    if [ "$STATUS" = "ACTIVE" ]; then
        echo "✅ SSL Certificate is ACTIVE!"
        break
    elif [ "$STATUS" = "FAILED_NOT_VISIBLE" ]; then
        echo "❌ SSL provisioning failed - check DNS configuration"
        break
    fi
    echo "Waiting 60 seconds..."
    sleep 60
done
```

## 🧪 Step 11: Test the Setup

Verify everything is working:

```bash
# Test health endpoint
echo "Testing backend health..."
curl -v https://$DOMAIN_NAME/health

# Test API endpoint
echo "Testing API..."
curl -v https://$DOMAIN_NAME/api/

# Test frontend
echo "Testing frontend..."
curl -I https://$DOMAIN_NAME/

# Test API documentation
echo "Testing API docs..."
curl -I https://$DOMAIN_NAME/docs
```

## 📊 Step 12: Monitor and Verify

Check your setup:

```bash
# List all components
echo "=== Load Balancer Components ==="
echo "URL Maps:"
gcloud compute url-maps list

echo "SSL Certificates:"
gcloud compute ssl-certificates list

echo "Backend Services:"
gcloud compute backend-services list

echo "Target Proxies:"
gcloud compute target-https-proxies list

echo "Forwarding Rules:"
gcloud compute forwarding-rules list --global

# Check logs
echo "=== Checking Load Balancer Logs ==="
gcloud logs read "resource.type=http_load_balancer" --limit=10
```

## 🔄 Step 13: Update Routing (Optional)

To modify traffic routing later:

```bash
# Edit the URL map file
nano /tmp/url-map.yaml

# Update the URL map
gcloud compute url-maps import aialchemy-url-map \
    --source=/tmp/url-map.yaml \
    --global
```

## 🚨 Troubleshooting

### Common Issues and Solutions:

**SSL Certificate stuck in PROVISIONING:**
```bash
# Check DNS propagation
nslookup $DOMAIN_NAME
dig $DOMAIN_NAME

# Verify DNS points to correct IP
RESOLVED_IP=$(dig +short $DOMAIN_NAME)
if [ "$RESOLVED_IP" = "$EXTERNAL_IP" ]; then
    echo "✅ DNS configured correctly"
else
    echo "❌ DNS mismatch: Expected $EXTERNAL_IP, got $RESOLVED_IP"
fi
```

**404 Errors:**
```bash
# Check URL map configuration
gcloud compute url-maps describe aialchemy-url-map --global

# Verify backend services are healthy
gcloud compute backend-services get-health aialchemy-api-backend --global
gcloud compute backend-services get-health aialchemy-frontend-backend --global
```

**Backend Service Errors:**
```bash
# Check Cloud Run service logs
gcloud logs read "resource.type=cloud_run_revision AND resource.labels.service_name=aialchemy-backend" --limit=20
gcloud logs read "resource.type=cloud_run_revision AND resource.labels.service_name=aialchemy-frontend" --limit=20
```

## 🧹 Cleanup (If Needed)

To remove all load balancer resources:

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

## 🎉 Final Access URLs

Once everything is configured:

- **Frontend**: `https://aialchemy.yourdomain.com`
- **Backend API**: `https://aialchemy.yourdomain.com/api/`
- **API Docs**: `https://aialchemy.yourdomain.com/docs`
- **Health Check**: `https://aialchemy.yourdomain.com/health`

## 📚 Additional Resources

- [Google Cloud Load Balancing Documentation](https://cloud.google.com/load-balancing/docs)
- [SSL Certificate Management](https://cloud.google.com/certificate-manager/docs)
- [Cloud Run with Load Balancers](https://cloud.google.com/run/docs/mapping-custom-domains)
- [URL Map Configuration](https://cloud.google.com/load-balancing/docs/url-map-concepts)