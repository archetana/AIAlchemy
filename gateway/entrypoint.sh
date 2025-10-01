#!/bin/sh
# Substitute environment variables in nginx configuration

set -e

echo "🔧 Configuring NGINX Gateway..."

# Get service URLs from environment or default values
BACKEND_URL=${BACKEND_URL:-"aialchemy-backend-url.a.run.app"}
FRONTEND_URL=${FRONTEND_URL:-"aialchemy-frontend-url.a.run.app"}

echo "📋 Service configuration:"
echo "  Backend URL:  $BACKEND_URL"
echo "  Frontend URL: $FRONTEND_URL"

# Remove https:// prefix if present
BACKEND_URL=$(echo $BACKEND_URL | sed 's|https://||')
FRONTEND_URL=$(echo $FRONTEND_URL | sed 's|https://||')

# Substitute variables in nginx configuration
sed -i "s/aialchemy-backend-url.a.run.app/$BACKEND_URL/g" /etc/nginx/templates/default.conf.template
sed -i "s/aialchemy-frontend-url.a.run.app/$FRONTEND_URL/g" /etc/nginx/templates/default.conf.template

# Copy the configured template to the final location
cp /etc/nginx/templates/default.conf.template /etc/nginx/conf.d/default.conf

echo "✅ NGINX Gateway configured successfully"

# Test nginx configuration
nginx -t

echo "🚀 Starting NGINX Gateway..."