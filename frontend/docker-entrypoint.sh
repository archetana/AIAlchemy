#!/bin/sh
set -e

echo "🚀 Starting AIAlchemy Frontend"

# Replace environment variables in built files
if [ -f /usr/share/nginx/html/static/js/main.*.js ]; then
    echo "🔧 Configuring environment variables"
    
    # Replace API base URL if provided
    if [ ! -z "$REACT_APP_API_BASE_URL" ]; then
        find /usr/share/nginx/html/static/js -name "*.js" -exec sed -i "s|PLACEHOLDER_API_URL|$REACT_APP_API_BASE_URL|g" {} +
    fi
    
    # Replace other environment variables as needed
    if [ ! -z "$REACT_APP_ENVIRONMENT" ]; then
        find /usr/share/nginx/html/static/js -name "*.js" -exec sed -i "s|PLACEHOLDER_ENVIRONMENT|$REACT_APP_ENVIRONMENT|g" {} +
    fi
fi

echo "🌐 Starting nginx server on port ${PORT:-8080}"

# Start nginx
exec nginx -g 'daemon off;'