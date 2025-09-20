# Multi-stage Dockerfile for React frontend
# Optimized for production deployment on Google Cloud Run with nginx

# Stage 1: Build stage
FROM node:18-alpine as builder

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --silent --only=production && \
    npm cache clean --force

# Copy source code
COPY . .

# Build application for production
ENV NODE_ENV=production
ENV GENERATE_SOURCEMAP=false
ENV REACT_APP_VERSION=$REACT_APP_VERSION

RUN npm run build

# Stage 2: Production stage with nginx
FROM nginx:alpine as production

# Install curl for health checks
RUN apk --no-cache add curl

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built application from builder stage
COPY --from=builder /app/build /usr/share/nginx/html

# Create startup script for Cloud Run
RUN cat > /docker-entrypoint.sh << 'EOF'
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

echo "🌐 Starting nginx server on port ${PORT:-80}"

# Start nginx
exec nginx -g 'daemon off;'
EOF

RUN chmod +x /docker-entrypoint.sh

# Create nginx configuration that works with Cloud Run
RUN cat > /etc/nginx/conf.d/default.conf << 'EOF'
server {
    listen 8080;
    server_name _;
    
    # Enable gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=63072000" always;
    
    # Root directory
    root /usr/share/nginx/html;
    index index.html;
    
    # Handle client-side routing
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    # Cache static assets
    location /static/ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # API proxy (if needed for CORS)
    location /api/ {
        if ($request_method = 'OPTIONS') {
            add_header 'Access-Control-Allow-Origin' '*';
            add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS, PUT, DELETE';
            add_header 'Access-Control-Allow-Headers' 'DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization';
            add_header 'Access-Control-Max-Age' 1728000;
            add_header 'Content-Type' 'text/plain; charset=utf-8';
            add_header 'Content-Length' 0;
            return 204;
        }
        
        proxy_pass ${REACT_APP_API_BASE_URL};
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Health check endpoint
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
    
    # Security - deny access to sensitive files
    location ~ /\. {
        deny all;
        access_log off;
        log_not_found off;
    }
    
    location ~ ~$ {
        deny all;
        access_log off;
        log_not_found off;
    }
}
EOF

# Expose port 8080 (Cloud Run requirement)
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Start application
ENTRYPOINT ["/docker-entrypoint.sh"]