#!/bin/sh
# Replace placeholders in nginx.conf with actual Cloud Run service URLs

echo "Setting up nginx configuration..."

# Replace BACKEND_HOST and FRONTEND_HOST placeholders
if [ -n "$BACKEND_HOST" ]; then
    sed -i "s/BACKEND_HOST/$BACKEND_HOST/g" /etc/nginx/nginx.conf
    echo "Backend host set to: $BACKEND_HOST"
else
    echo "Warning: BACKEND_HOST environment variable not set"
fi

if [ -n "$FRONTEND_HOST" ]; then
    sed -i "s/FRONTEND_HOST/$FRONTEND_HOST/g" /etc/nginx/nginx.conf
    echo "Frontend host set to: $FRONTEND_HOST"
else
    echo "Warning: FRONTEND_HOST environment variable not set"
fi

echo "Starting nginx..."
exec nginx -g 'daemon off;'