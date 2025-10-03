#!/bin/bash
# Cleanup Google Cloud Load Balancer Resources
# Run this script to remove old load balancer components

set -e

# Configuration
PROJECT_ID="${PROJECT_ID:-automatic-asset-472710-b6}"
REGION="${REGION:-us-central1}"

echo "🧹 Cleaning up Google Cloud Load Balancer resources..."
echo "Project: $PROJECT_ID"
echo "Region: $REGION"

# Set project
gcloud config set project $PROJECT_ID

echo "📋 Checking existing resources..."

# Function to safely delete resources
safe_delete() {
    local resource_type="$1"
    local resource_name="$2" 
    local additional_flags="$3"
    
    if gcloud compute $resource_type describe $resource_name $additional_flags &>/dev/null; then
        echo "🗑️  Deleting $resource_type: $resource_name"
        gcloud compute $resource_type delete $resource_name $additional_flags --quiet
        echo "✅ Deleted $resource_type: $resource_name"
    else
        echo "ℹ️  $resource_type $resource_name not found (already deleted or doesn't exist)"
    fi
}

# Delete forwarding rules first
echo ""
echo "🔗 Cleaning up forwarding rules..."
safe_delete "forwarding-rules" "aialchemy-http-rule" "--global"
safe_delete "forwarding-rules" "aialchemy-https-rule" "--global"

# Delete target proxies
echo ""
echo "🎯 Cleaning up target proxies..."
safe_delete "target-http-proxies" "aialchemy-http-proxy" ""
safe_delete "target-https-proxies" "aialchemy-https-proxy" ""

# Delete URL maps
echo ""
echo "🗺️  Cleaning up URL maps..."
safe_delete "url-maps" "aialchemy-url-map" "--global"
safe_delete "url-maps" "aialchemy-url-map-no-domain" "--global"

# Delete SSL certificates
echo ""
echo "🔒 Cleaning up SSL certificates..."
safe_delete "ssl-certificates" "aialchemy-ssl-cert" "--global"

# Delete backend services
echo ""
echo "🏗️  Cleaning up backend services..."
safe_delete "backend-services" "aialchemy-api-backend" "--global"
safe_delete "backend-services" "aialchemy-frontend-backend" "--global"

# Delete network endpoint groups
echo ""
echo "🔗 Cleaning up network endpoint groups..."
safe_delete "network-endpoint-groups" "aialchemy-backend-neg" "--region=$REGION"
safe_delete "network-endpoint-groups" "aialchemy-frontend-neg" "--region=$REGION"
safe_delete "network-endpoint-groups" "backend-neg" "--region=$REGION"
safe_delete "network-endpoint-groups" "frontend-neg" "--region=$REGION"

# Delete health checks (if any exist)
echo ""
echo "🏥 Cleaning up health checks..."
safe_delete "health-checks" "backend-health-check" ""
safe_delete "health-checks" "frontend-health-check" ""

echo ""
echo "✅ Load balancer cleanup complete!"
echo ""
echo "📊 Remaining Cloud Run services (these are kept):"
gcloud run services list --region=$REGION --filter="metadata.name~aialchemy"

echo ""
echo "💰 Estimated monthly savings: ~$25-40"
echo ""
echo "🎯 Next steps:"
echo "1. Deploy nginx gateway: ./deploy-nginx-gateway.sh"
echo "2. Test the new gateway endpoints"
echo "3. Update your deployment workflow if needed"
echo ""
echo "🔙 To restore load balancer later:"
echo "   Use the original deployment script with DOMAIN_NAME set"