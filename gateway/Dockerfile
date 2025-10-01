# AIAlchemy NGINX Gateway
# Routes traffic between frontend and backend Cloud Run services

FROM nginx:alpine

# Install curl for health checks
RUN apk --no-cache add curl

# Create directory for nginx configuration
RUN mkdir -p /etc/nginx/templates

# Copy nginx configuration template
COPY nginx.conf /etc/nginx/templates/default.conf.template

# Create entrypoint script to substitute environment variables
COPY entrypoint.sh /docker-entrypoint.d/50-substitute-urls.sh
RUN chmod +x /docker-entrypoint.d/50-substitute-urls.sh

# Expose port 8080 for Cloud Run
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]