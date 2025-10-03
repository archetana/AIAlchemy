FROM nginx:alpine

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Copy setup script
COPY setup-nginx.sh /setup-nginx.sh
RUN chmod +x /setup-nginx.sh

# Expose port 8080
EXPOSE 8080

# Use setup script as entrypoint to replace placeholders
ENTRYPOINT ["/setup-nginx.sh"]